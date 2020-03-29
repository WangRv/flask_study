class BaseField:
    def __init__(self, name, column_type):
        self.name = name
        self._type = column_type

    def __str__(self):
        return f"<{self.__class__.__name__}>:<{self.name}>"


class StrField(BaseField):
    def __init__(self, name):
        super(StrField, self).__init__(name, "varchar(100)")


class Base(type):
    def __new__(mcs, name, base, attr):
        if name == "Model":
            return type.__new__(mcs, name, base, attr)
        else:
            mapping = {}
            for filed_name, filed in attr.items():
                if isinstance(filed, BaseField):
                    mapping[filed_name] = filed
            for filed_name in mapping.keys():
                attr.pop(filed_name)
        attr["__mappings__"] = mapping
        attr["__table__"] = name
        return type.__new__(mcs, name, base, attr)


class Model(dict, metaclass=Base):
    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.__mappings__:
                raise KeyError(f"Not a filed name {key}")
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(rf"Model object has no attribute {item}")

    def __setattr__(self, key, value):
        if key in self.__mappings__:
            self[key] = value
        else:
            raise AttributeError(f"Not a filed<{key}>")

    def save(self):
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))
        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
        print('SQL: %s' % sql)
        print('ARGS: %s' % str(args))
        return sql


class User(Model):
    name = StrField("name")


if __name__ == '__main__':
    u = User(name="test")
    print(u.save())
