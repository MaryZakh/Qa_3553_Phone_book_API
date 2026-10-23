import requests

class APIClient:
    def __init__(self,base_url,token = None):
        self.base_url = base_url
        self.session = requests.Session()

        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _url(self, path):
        return f"{self.base_url}{path}"

    def get(self,path, **kwargs):
        return self.session.get(self._url(path), **kwargs)

    def post(self,path, **kwargs):
        return self.session.post(self._url(path), **kwargs)

    def put(self,path, **kwargs):
        return self.session.put(self._url(path), **kwargs)

    def delete(self,path, **kwargs):
        return self.session.delete(self._url(path), **kwargs)

    def close(self):
        self.session.close()