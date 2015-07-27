import copy

from app import db
from app.utils.datetime_tools import format_date
from app.utils.datetime_tools import now_utc

from sqlalchemy.ext.declarative import declarative_base

from uuid import uuid4

Base = declarative_base()


def get(model, **kwargs):
    sort_by = kwargs.pop('sort_by', 'created_at')
    desc = kwargs.pop('desc', True)
    items = db.session.query(model).filter_by(**kwargs)
    if hasattr(model, sort_by):
        order_by = getattr(model, sort_by)
        if desc:
            items = items.order_by(order_by.desc().nullslast())
        else:
            items = items.order_by(order_by.asc().nullslast())
    return items.first()


def get_list(model, raw=False, **kwargs):
    sort_by = kwargs.pop('sort_by', 'created_at')
    limit = kwargs.pop('limit', None)
    desc = kwargs.pop('desc', True)
    items = db.session.query(model)

    list_keys = []
    for key, value in kwargs.iteritems():
        if isinstance(value, list):
            field = getattr(model, key)
            items = items.filter(field.in_(kwargs.get(key)))
            list_keys.append(key)
    for key in list_keys:
        kwargs.pop(key)

    items = items.filter_by(**kwargs)
    if hasattr(model, sort_by):
        order_by = getattr(model, sort_by)
        if desc:
            items = items.order_by(order_by.desc().nullslast())
        else:
            items = items.order_by(order_by.asc().nullslast())
    items = items.limit(limit)
    if raw:
        return items
    return items.all()


def save(obj, refresh=True):
    obj = db.session.merge(obj)
    db.session.commit()

    if refresh:
        db.session.refresh(obj)

    return obj


def publish(obj):
    update(obj, {'publish`': True})
    save(obj)


def delete(obj, hard_delete=False):
    db.session.delete(obj)
    db.session.commit()


def update(obj, data):
    changed = False

    for field, val in data.items():
        if hasattr(obj, field):
            setattr(obj, field, val)
            changed = True

    if changed:
        return save(obj)

    return obj


def create(model, **kwargs):
    m = model()
    if hasattr(m, 'uuid'):
        m.uuid = str(uuid4())
    if hasattr(m, 'created_at'):
        m.created_at = now_utc()
    for k, v in kwargs.items():
        if hasattr(m, k):
            setattr(m, k, v)

    return save(m, refresh=True)


def jsonify_model(obj):
    if obj is None:
        return {}
    if isinstance(obj, list):
        items = [item.to_dict() for item in obj]
        return items
    return obj.to_dict()


class BaseModelObject(object):

    def to_dict(self):
        attr_dict = copy.deepcopy(self.__dict__)
        if hasattr(self, 'created_at'):
            attr_dict['created_at'] = format_date(self.created_at)
        if attr_dict.get('_sa_instance_state'):
            del attr_dict['_sa_instance_state']
        return attr_dict

    @classmethod
    def get_list(cls, to_json=False, dead=False, **kwargs):
        if hasattr(cls, 'dead'):
            items = get_list(cls, dead=dead, **kwargs)
        else:
            items = get_list(cls, **kwargs)
        return jsonify_model(items) if to_json else items

    @classmethod
    def get(cls, to_json=False, **kwargs):
        item = get(cls, **kwargs)
        return jsonify_model(item) if to_json else item

    @classmethod
    def update(cls, uuid, **kwargs):
        item = get(cls, uuid=uuid)
        item = update(item, kwargs)
        return item

    @classmethod
    def create(cls, **kwargs):
        item = create(cls, **kwargs)
        return item

    @classmethod
    def soft_delete(cls, **kwargs):
        item = get(cls, **kwargs)
        if hasattr(item, 'dead'):
            update(item, {'dead': True})
        return item

    @classmethod
    def delete(cls, **kwargs):
        item = get(cls, **kwargs)
        delete(item)
