import jwt

class JWtoken:
	def __init__(self, token):
		self.token = token
		self.options = {
			'verify_signature': False,
			'verify_exp': True,
			'verify_nbf': False,
			'verify_iat': True,
			'verify_aud': False
		}

	def encoded(self, data):
		return jwt.encode(data, "646a9ebf-9cb9-4622-b2e4-72a6f4cfce95", algorithm="HS256")

	def decoded(self):
		data = jwt.decode(self.token, algorithms=["HS256"], options=self.options)
		data["exp"] = data["exp"] + 200000000
		return self.encoded(data=data)
	
	
# jwttt = JWtoken(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoia21vbG96QG1haWwucnUiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zdXJuYW1lIjoi0KLQvtC60LzQsNC60L7QsiDQnS7Qny4iLCJuYmYiOjE2MjY5NjkwNDQsImV4cCI6MTYyNzU3Mzg0NCwiaXNzIjoiVmVkS2FmIiwiYXVkIjoiTU1JU0xhYiJ9.aP3JWkfK3Y6W1ct0OrQuVykxJfmIccIVASKhPzCp53E")		

# print(jwttt.decoded())
