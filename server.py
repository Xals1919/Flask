from typing import Type

from flask import Flask, request, jsonify, Response
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Ticket, Session
from schema import CreateTicket, UpdateTicket

app = Flask('app')


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response: Response):
    request.session.close()
    return response


class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response


def get_ticket_by_id(ticket_id: int):
    ticket = request.session.query(Ticket).get(ticket_id)
    if ticket is None:
        raise HttpError(404, "ticket not found")
    return ticket


def add_ticket(ticket: Ticket):
    try:
        request.session.add(ticket)
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, "ticket already exists")


def validate_json(json_data: dict, schema_class: Type[CreateTicket] | Type[UpdateTicket]):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop('ctx', None)
        raise HttpError(400, error)



class UserView(MethodView):
    def get(self, ticket_id: int):
        ticket = get_ticket_by_id(ticket_id)
        return jsonify(ticket.dictionary)

    def post(self):
        ticket_data = validate_json(request.json, CreateTicket)
        ticket = Ticket(**ticket_data)
        add_ticket(ticket)
        return jsonify(ticket.dictionary)

    def patch(self, ticket_id: int):
        ticket_data = validate_json(request.json, UpdateTicket)
        ticket = get_ticket_by_id(ticket_id)
        for field, value in ticket_data.items():
            setattr(ticket, field, value)
        add_ticket(ticket)
        return jsonify(ticket.dictionary)

    def delete(self, ticket_id: int):
        ticket = get_ticket_by_id(ticket_id)
        request.session.delete(ticket)
        request.session.commit()
        return jsonify({'status': 'deleted'})


user_view = UserView.as_view('user_view')

app.add_url_rule(rule='/ticket/<int:ticket_id>',
                 view_func=user_view,
                 methods=['GET', 'PATCH', 'DELETE'])

app.add_url_rule(rule='/ticket/',
                 view_func=user_view,
                 methods=['POST'])

if __name__ == '__main__':
    app.run()
