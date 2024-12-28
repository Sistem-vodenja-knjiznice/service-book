import graphene

import books.schema


class Query(books.schema.Query, graphene.ObjectType):
    # Combine the queries from different apps
    pass

schema = graphene.Schema(query=Query)
