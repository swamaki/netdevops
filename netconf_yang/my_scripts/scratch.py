from ncclient import manager

m = manager.connect(host='169.254.224.21', port=830, username='admin', password='cisco123', device_params={'name': 'csr'})

print(m.server_capabilities)
