from ariadne import QueryType, graphql_sync, make_executable_schema, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

type_defs = """
    type Query {
        hello: String!
        students(id : Int!) : Student!
        classes(cid : Int!) : Classinfo!
    }
    type Mutation {
        create_student(name: String): Student!
        create_class(name: String!): Classinfo!
        add_student_class(sid: Int!, cid: Int!) : Classinfo!
        
    }
    type Student {
        s_id : Int
        name : String
    }

    type Classinfo{
        c_id : Int
        name : String
        class_student : [Student!]
    }
"""
mutation = MutationType()
query = QueryType()

students1 = []
classes1 = []

stu_id = 1238125
cla_id = 1238125


@query.field("hello")
def resolve_hello(_, info):
    print("i am Echo")
    return "Hello, Echo!"

@mutation.field("create_student")
def create_student(_, info, name):
    global stu_id
    stu_id += 1
    global students1
    students1.append({"s_id":stu_id, "name" : name})
    return {"s_id":stu_id, "name" : name}

@query.field("students")
def students(_, info, id):
    try:
         for student in students1:
             if student['s_id'] == id:
                 return student
    except:
        print('error/exception')
        
@mutation.field("create_class")
def create_class(_, info, name):
    global cla_id
    cla_id += 1
    classes1.append({
        'c_id': cla_id,
        'name': name
    })
    return{"c_id": cla_id, "name": name}

@query.field("classes")               
def classes(_, info, cid):
    # try:
    for classinfo in classes1:
        if classinfo['c_id'] == cid:
            print(classinfo)
            return {'c_id': cid,'name': classinfo['name']}
    # except:
        # print('error') 
    

@mutation.field("add_student_class")       
def add_student_class(_, info, sid, cid):
    # find student info
    for student in students1 :
        if student['s_id'] == sid:
            s_name = student['name']
    # find class info
    for classinfo in classes1:
        if classinfo['c_id'] == cid:
            c_name = classinfo['name']
            class_students = classinfo.get('class_student', [])
            class_students.append({'s_id': sid, 'name': s_name})
            classinfo['class_student'] = class_students
    return {'c_id': cid, 'name': c_name, 'class_student': class_students}

         


schema = make_executable_schema(type_defs, [query, mutation])

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)