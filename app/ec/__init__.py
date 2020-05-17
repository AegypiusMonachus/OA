from flask import Blueprint
ec_0_1_blueprint = Blueprint('ec_0_1', __name__)


@ec_0_1_blueprint.before_request
def before_request():
    pass


@ec_0_1_blueprint.after_request
def after_request(response):
    return response

from flask_restful import Api
api = Api(ec_0_1_blueprint)

from .resources.validate import ValidateAPI
api.add_resource(ValidateAPI, '/Validate')

















