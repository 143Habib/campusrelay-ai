from app.database import connection

TICKET={
    'title':'Internet disconnecting in lab',
    'description':'The laboratory Wi-Fi network has stopped working and many students are unable to submit coursework.',
    'location':'IT Lab 204',
    'category':'IT',
    'priority':'Medium',
}


def test_student_can_create_comment_and_see_owned_ticket(student):
    client,h=student
    create=client.post('/api/tickets',json=TICKET,headers=h)
    assert create.status_code==201,create.text
    data=create.json()
    assert data['ref'].startswith('CR-')
    tid=data['id']
    detail=client.get(f'/api/tickets/{tid}')
    assert detail.status_code==200
    assert detail.json()['ticket']['description']==TICKET['description']
    assert detail.json()['allowed_next']==[]
    comment=client.post(f'/api/tickets/{tid}/comments',json={'note':'Still unable to connect today.'},headers=h)
    assert comment.status_code==201
    assert len(client.get(f'/api/tickets/{tid}').json()['events'])==2
    dashboard=client.get('/api/dashboard').json()
    assert dashboard['scope']=='own'
    assert dashboard['total']>0


def test_student_cannot_read_other_student_ticket(student):
    client,h=student
    # seeded #4 is owned by Mina and must be indistinguishable from missing tickets.
    assert client.get('/api/tickets/4').status_code==404
    assert client.get('/api/tickets/99999').status_code==404
    assert client.post('/api/tickets/4/comments',json={'note':'Hello'},headers=h).status_code==404
    assert client.patch('/api/tickets/2/status',json={'status':'Resolved'},headers=h).status_code==403
    assert client.patch('/api/tickets/2/assignee',json={'assignee_id':2},headers=h).status_code==403
    assert client.get('/api/users/assignees').status_code==403
    assert client.get('/api/export/tickets.csv').status_code==403
    listing=client.get('/api/tickets?page_size=50').json()
    assert all(t['creator_id']==1 for t in listing['items'])


def test_staff_validated_workflow_assignment_and_reopen(staff):
    client,h=staff
    created=client.post('/api/tickets',json=TICKET,headers=h).json()
    tid=created['id']
    # A ticket cannot skip the In Progress phase or move backward arbitrarily.
    assert client.patch(f'/api/tickets/{tid}/status',json={'status':'Resolved'},headers=h).status_code==409
    assert client.patch(f'/api/tickets/{tid}/status',json={'status':'In Progress','note':'Work started'},headers=h).status_code==200
    assert client.patch(f'/api/tickets/{tid}/status',json={'status':'Resolved','note':'Repaired'},headers=h).status_code==200
    assert client.patch(f'/api/tickets/{tid}/status',json={'status':'Reopened','note':'Issue returned'},headers=h).status_code==200
    assert client.patch(f'/api/tickets/{tid}/status',json={'status':'In Progress'},headers=h).status_code==200
    assert client.patch(f'/api/tickets/{tid}/assignee',json={'assignee_id':1},headers=h).status_code==422
    assert client.patch(f'/api/tickets/{tid}/assignee',json={'assignee_id':2},headers=h).status_code==200
    info=client.get(f'/api/tickets/{tid}').json()
    assert info['ticket']['status']=='In Progress'
    assert info['ticket']['assignee_id']==2
    assert [x['event_type'] for x in info['events']].count('status')==4


def test_staff_csv_export(staff):
    client,h=staff
    result=client.get('/api/export/tickets.csv')
    assert result.status_code==200
    assert 'text/csv' in result.headers['content-type']
    assert 'creator_name' in result.text
    assert 'CR-2026-0001' in result.text


def test_filters_pagination(staff):
    client,_=staff
    result=client.get('/api/tickets?category=IT&status=Resolved&page_size=2&page=1')
    assert result.status_code==200
    data=result.json()
    assert data['page_size']==2
    assert all(t['category']=='IT' and t['status']=='Resolved' for t in data['items'])
    assert client.get('/api/tickets?status=Unknown').status_code==422
    assert client.get('/api/tickets?page_size=200').status_code==422


def test_invalid_ticket_data_rejected(student):
    client,h=student
    bad=TICKET|{'title':'Hi'}
    assert client.post('/api/tickets',json=bad,headers=h).status_code==422
    bad=TICKET|{'category':'Exploit'}
    assert client.post('/api/tickets',json=bad,headers=h).status_code==422
    bad=TICKET|{'status':'Resolved'}
    assert client.post('/api/tickets',json=bad,headers=h).status_code==422


def test_metrics_are_derived_from_database(student):
    client,h=student
    initial=client.get('/api/dashboard').json()
    client.post('/api/tickets',json=TICKET,headers=h)
    later=client.get('/api/dashboard').json()
    assert later['total']==initial['total']+1
    assert later['status_counts']['Open']==initial['status_counts']['Open']+1


def test_admin_has_staff_capabilities(admin):
    client,h=admin
    assert client.get('/api/dashboard').json()['scope']=='all'
    assert client.get('/api/users/assignees').status_code==200
    assert client.post('/api/tickets',json=TICKET,headers=h).status_code==201
