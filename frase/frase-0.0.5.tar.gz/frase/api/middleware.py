import jwt
import falcon

from frase.settings import KEYCLOAK_PUBLIC_KEY, VERIFY_SIGNATURE


class AuthenticationMiddleware:
    def __parse_auth_header(self, header):
        if header:
            data = header.split(" ")
            if len(data) == 2:
                return data

    def __parse_token(self, req, token_type, token_data):
        if token_type.lower() == "public":
            payload = {}
            try:
                if VERIFY_SIGNATURE:
                    payload = jwt.decode(
                        token_data,
                        KEYCLOAK_PUBLIC_KEY,
                        algorithms=["RS256"],
                    )
                else:
                    payload = jwt.decode(jwt=token_data, options={"verify_signature": False}, algorithms=["RS256"])

            except Exception as e:
                raise falcon.HTTPBadRequest('Bad request', str(e))

            current_resource_name = payload.get("azp")
            resource_access = payload.get("resource_access") or {}
            access = resource_access.get(current_resource_name)
            if access is None:
                raise falcon.HTTPBadRequest('Bad request',
                                            "User does not have right permitions to access this resource")

            req.context["user"] = payload
            req.context["access"] = access

        else:
            raise falcon.HTTPBadRequest('Bad request', "Can not use token with type: {}".format(token_type))

    def process_resource(self, req, resp, resource, params):
        if req.method == "OPTIONS":
            pass
        else:
            auth = req.get_header("authorization")

            token = self.__parse_auth_header(auth)
            if token is None:
                raise falcon.HTTPBadRequest('Bad request', "Auth header not in right format")
            else:
                payload = self.__parse_token(req=req, token_type=token[0], token_data=token[1])

