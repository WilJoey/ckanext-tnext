import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import class_mapper

suggest_table = None
Suggest = None


def make_uuid():
    return unicode(uuid.uuid4())


def init_db(model):
    class _Suggest(model.DomainObject):

        @classmethod
        def get(cls, **kw):
            ''' Finds a single entity in the register. '''
            query = model.Session.query(cls).autoflush(False)
            return query.filter_by(**kw).firset()

        @classmethod
        def suggests(cls, limit, offset):
            query = model.Session.query(cls).autoflush(False)
            search = {}
            search['is_enabled'] = True
            query = query.filter_by(is_enabled=True)
            query = query.order_by(sa.desc(cls.created))
            #query = query.limit(limit)
            #query = query.offset(offset)
            '''
            suggest_list = []
            for sg in query.all():
                aps = {}
                aps['id'] = sg.id
                aps['title'] = sg.title
                aps['suggester'] = sg.suggester
                aps['dsname'] = sg.suggest_name
                aps['columns'] = sg.suggest_columns
                aps['views'] = sg.views
                aps['created'] = sg.created
                suggest_list.append(aps)
               
            return suggest_list
            '''
            return query.all()

    global Suggest
    Suggest = _Suggest
    # Create the SUGGEST table.
    sql = '''
CREATE TABLE IF NOT EXISTS ckanext_suggest
(
    id text NOT NULL,
    title text,
    content text,
    suggester text,
    suggest_name text,
    suggest_columns text,
    created timestamp without time zone,
    upper text,
    user_id text NOT NULL,
    is_enabled boolean NOT NULL DEFAULT true,
    views integer NOT NULL DEFAULT 1,
    CONSTRAINT pk_ckanext_suggest PRIMARY KEY (id )
);
'''
    conn =  model.Session.connection()
    try:
        conn.execute(sql)
    except sa.exc.ProgrammingError:
        pass
    model.Session.commit()

    types = sa.types
    global suggest_table
    suggest_table = sa.Table('ckanext_suggest', model.meta.metadata,
        sa.Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
        sa.Column('title', types.UnicodeText, default=u''),
        sa.Column('content', types.UnicodeText, default=u''),
        sa.Column('suggester', types.UnicodeText, default=u''),
        sa.Column('suggest_name', types.UnicodeText, default=u''),
        sa.Column('suggest_columns', types.UnicodeText, default=u''),
        sa.Column('created', types.UnicodeText, default=datetime.datetime.utcnow),
        sa.Column('upper', types.UnicodeText, default=u''),
        sa.Column('user_id', types.UnicodeText, default=u''),
        sa.Column('is_enabled', types.Boolean, default=True),
        sa.Column('views', types.Integer, default=1)
    )

    model.meta.mapper(Suggest, suggest_table)

def table_dictize(obj, context, **kw):
    '''Get any model object and represent it as a dict'''
    result_dict = {}

    #model = context["model"]
    #session = model.Session

    if isinstance(obj, sa.engine.base.RowProxy):
        fields = obj.keys()
    else:
        ModelClass = obj.__class__
        table = class_mapper(ModelClass).mapped_table
        fields = [field.name for field in table.c]

    for field in fields:
        name = field
        if name in ('current', 'expired_timestamp', 'expired_id'):
            continue
        if name == 'continuity_id':
            continue
        value = getattr(obj, name)
        if value is None:
            result_dict[name] = value
        elif isinstance(value, dict):
            result_dict[name] = value
        elif isinstance(value, int):
            result_dict[name] = value
        elif isinstance(value, datetime.datetime):
            result_dict[name] = value.isoformat()
        elif isinstance(value, list):
            result_dict[name] = value
        else:
            result_dict[name] = unicode(value)

    #result_dict.update(kw)

    ##HACK For optimisation to get metadata_modified created faster.
    context['metadata_modified'] = max(result_dict.get('revision_timestamp', ''),
                                       context.get('metadata_modified', ''))

    return result_dict































