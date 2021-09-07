ENVIRONMENT = 'PRODUCTION'
base_urls = {
  'MVP': 'https://cs-platform-306304.et.r.appspot.com/api',
  'STAGING': 'https://staging-dot-cs-platform-306304.et.r.appspot.com/api/v1',
  'PRODUCTION': 'https://api-dot-cs-platform-306304.et.r.appspot.com/api/v1',
  'LOCAL': 'http://localhost:8080/api/v1'
}
APP_URL = base_urls[ENVIRONMENT]
