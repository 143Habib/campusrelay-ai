from pathlib import Path
from app.ml import CampusClassifier, CATEGORIES, read_labeled


def test_model_uses_distinct_holdout_and_has_measured_evaluation():
    model=CampusClassifier()
    train_x,train_y=read_labeled(model.root/'data'/'train.csv')
    test_x,test_y=read_labeled(model.root/'data'/'holdout.csv')
    assert model.metrics['train_examples']==len(train_x)==380
    assert model.metrics['holdout_examples']==len(test_x)==50
    assert not set(test_x).intersection(train_x)
    assert 0.5<=model.metrics['accuracy']<=1
    assert len(model.metrics['confusion_matrix'])==len(CATEGORIES)
    assert set(train_y)==set(test_y)==set(CATEGORIES)


def test_recommendation_contains_explanation_and_override():
    model=CampusClassifier()
    pred=model.suggest('Exposed electrical wires are sparking near the stairwell and this is dangerous.')
    assert pred['priority']=='High'
    assert pred['human_override'] is True
    assert pred['category'] in CATEGORIES
    assert 0<=pred['confidence']<=1
    assert len(pred['alternatives'])==3
    assert pred['explanation']


def test_ai_endpoint_authenticated(student):
    client,h=student
    a=client.post('/api/ai/suggest',json={'text':'My university student portal login is not working today.'},headers=h)
    assert a.status_code==200
    assert a.json()['category'] in CATEGORIES
    metrics=client.get('/api/ai/model-card').json()
    assert 'limitations' in metrics and metrics['holdout_examples']==50
    assert client.post('/api/ai/suggest',json={'text':'too short'},headers=h).status_code==422
