from commands import google

g = google.Google()

print(g.description)
print(g.bindings[0].match("g"))