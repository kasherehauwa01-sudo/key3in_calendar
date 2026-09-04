import pytest
pytestmark = pytest.mark.asyncio
async def auth(client,login="anna",name="Анна"):
    response=await client.post("/api/auth/register",json={"login":login,"pin":"1234","name":name})
    return {"Authorization":f"Bearer {response.json()['token']}"}
async def test_registration_login_and_settings(client):
    headers=await auth(client);assert (await client.get('/api/users/me',headers=headers)).json()['name']=='Анна'
    updated=await client.put('/api/users/me',headers=headers,json={'name':'Аня','color':'#0000ff'});assert updated.json()['color']=='#0000ff'
    login=await client.post('/api/auth/login',json={'login':'ANNA','pin':'1234'});assert login.status_code==200
    assert (await client.post('/api/auth/login',json={'login':'anna','pin':'9999'})).status_code==401
async def test_multiple_users_crud_search_and_empty(client):
    anna=await auth(client);boris=await auth(client,'boris','Борис')
    assert (await client.put('/api/notes/2026-09-04',headers=anna,json={'text':'Привет 😊'})).status_code==200
    assert (await client.put('/api/notes/2026-09-04',headers=boris,json={'text':'Общая дата'})).status_code==200
    monthly=await client.get('/api/notes',headers=anna,params={'year':2026,'month':9});assert len(monthly.json())==2
    assert {n['user_name'] for n in monthly.json()}=={'Анна','Борис'}
    found=await client.get('/api/notes/search',headers=anna,params={'q':'прив'});assert len(found.json())==1
    assert (await client.put('/api/notes/2026-09-04',headers=anna,json={'text':' '})).status_code==204
    assert len((await client.get('/api/notes/2026-09-04',headers=boris)).json())==1
    assert (await client.delete('/api/notes/2026-09-05',headers=anna)).status_code==204
async def test_validation_and_auth(client):
    assert (await client.get('/api/notes',params={'year':2026,'month':9})).status_code==401
    assert (await client.post('/api/auth/register',json={'login':'a','pin':'12','name':''})).status_code==422
    headers=await auth(client);assert (await client.put('/api/notes/2026-09-04',headers=headers,json={'text':'x'*20001})).status_code==422
