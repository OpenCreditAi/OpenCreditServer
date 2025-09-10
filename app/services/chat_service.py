from typing import List
from flask import jsonify
from app import db
from app.models import User, Loan
from app.models.message import Message


class ChatService:
    def get_messages(self, loan_id):
        messages = (
            db.session.query(Message)
            .filter_by(loan_id=loan_id)
            .order_by(Message.sent_at)
            .all()
        )

        return self.__jsonify_messages(messages)

    @staticmethod
    def __jsonify_messages(messages: List[Message]):
        message_list = []
        for message in messages:
            message_data = message.to_dict()

            message_list.append(message_data)

        return jsonify(message_list)

    def new_message(self, loan_id, sender_email, text: str):
        user: User = User.query.filter_by(email=sender_email).first()
        if not user:
            raise ValueError("Sender user not found")

        loan: Loan = Loan.query.filter_by(id=loan_id).first()
        if not loan:
            raise ValueError("Loan not found")

        message = Message(loan=loan, sender=user, message=text)
        db.session.add(message)
        db.session.commit()