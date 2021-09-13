from __future__ import annotations

import logging
import traceback
from typing import Dict, List, Type

import minio
from fastapi import FastAPI
from fastapi.responses import Response

from .datastructure import (GlobalContext, LoadTemplateBody, MinioCnfigure,
                            PublipostBody, S3Path)
from .template_db import TemplateDB, TemplateType


def EnablePublipost(app: FastAPI, template_class: Type[TemplateType]) -> FastAPI:
    context = GlobalContext()

    # in memory database
    # rebuilded at each boot
    db = TemplateDB(template_class)
    @app.post('/configure')
    def configure(data: MinioCnfigure):
        try:
            # TODO: should have an S3 interface here
            minio_client = minio.Minio(
                data.host, data.access_key, data.pass_key, secure=data.secure)
            # checking that the instance is correct
            minio_client.list_buckets()
            context.s3_client = minio_client
            db.set_s3_client(minio_client)
            return {'error': False}, 200
        except:
            return {'error': True}, 400


    @app.post('/load_templates')
    def load_template(data: List[LoadTemplateBody]):
        success = []
        failed = []
        for template_infos in data:
            try:
                template = db.add_template(S3Path(
                    template_infos.bucket_name, template_infos.template_name
                ),
                    template_infos.exposed_as
                )
                success.append({
                    'template_name': template_infos.exposed_as,
                    'fields': template.fields
                })
            except:
                logging.error(traceback.format_exc())
                failed.append(
                    {'template_name': template_infos.exposed_as}
                )
        return {
            'success': success,
            'failed': failed
        }


    @app.post('/get_placeholders')
    def get_placeholders(data: Dict[str, str]) -> List[str]:
        return db.get_fields(data['name'])


    @app.post('/publipost')
    def publipost(body: PublipostBody):
        output = None
        response = {'error': True}, 500
        try:
            # don't actually know if will get used
            options = body.options or ['pdf']
            # push_result = body.get('push_result', True)
            # TODO:
            push_result = True
            if body.template_name not in db.get_containers():
                db.add_template(S3Path(
                    body.bucket_name, body.r_template_name,
                ),
                    # template_name is same as exposed_as here
                    body.template_name,
                )
            # always render to pdf now
            output = db.render_template(body.template_name, body.data, options)
            if push_result:
                # should make abstraction to push the result here
                length = len(output.getvalue())
                output.seek(0)
                context.s3_client.put_object(
                    body.output_bucket, body.output_name, output, length=length
                )
                response = {'error': False}
            else:
                # not used for now
                # should push the file back
                response = {'result': 'OK'}
        except Exception as e:
            logging.error(traceback.format_exc())

        return response


    @app.get('/list')
    def get_templates():
        return {
            key: value.pulled_at for key, value in db.get_containers().items()
        }


    @app.delete('/remove_template')
    def remove_template(data: Dict[str, str]):
        try:
            template_name: str = data['template_name']
            db.delete_template(template_name)
            return {'error': False}
        except:
            return {'error': True}, 400


    @app.get('/live')
    def is_live():
        return Response('OK', 200) if context.s3_client is not None else Response('KO', 402)


    return app


def make_connector(template_class: TemplateType) -> FastAPI:
    app = FastAPI()
    return EnablePublipost(app, template_class)