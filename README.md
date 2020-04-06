# drf-guard

Flexible and simple to use permissions for Django REST Framework(DRF). Works with both class based DRF permissions, Django permissions and Django groups.

## Requirements
- Python >= 3.5
- Django >= 1.11
- Django REST Framework >= 3.5

## Installing
```py
pip install drf-guard
```

## Getting started
Using `drf-guard` is very simple, below is an example
```py
# views.py

# Import operators & permissions from drf_guard
from drf_guard.operators import And, Or, Not
from drf_guard.permissions import HasRequiredGroups, HasRequiredPermissions


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    # Use drf_guard permissions here
    permission_classes = (HasRequiredGroups, HasRequiredPermissions)
    
    # Now guard your API with groups and permissions as you wish
    groups_and_permissions = {
         'GET': {
             'list': {
                 # To access this the user must belongs to admin or client group
                 'groups': ['admin', Or, 'client'],
                 'permissions': [IsAuthenticated]  # Also the user must be authenticated
             },
             'retrieve': {
                 'groups': [Not, 'admin'],  # The user must not be in admin group
                 'permissions': [IsAuthenticated, And, IsAllowedUser]  # MUst be authenticated and allowed
             },
         },

         'PUT': {
             'groups': ['__all__'],  # Belongs to any group
             'permissions': [IsAuthenticated, And, IsAdmin]  # By now this should be obvious
         },

         'PATCH': {
             'groups': ['client', And, Not, 'admin'],  # User belongs to client and not admin group
             'permissions': [IsAuthenticated, IsAllowedUser]  # This is = [IsAuthenticated, And, IsAllowedUser]
         },
         
         'DELETE': {
             'groups': ['client', Or, [Not, 'client', And, 'admin']],  # You can basically do any combination
             'permissions': [IsAuthenticated]
         }
    }
```

What's important here is to know what goes into groups and permissions
- Groups takes group names and Django group objects, so you can use those operators however you want with these two, you can even mix the two types together, e.g
```py
'groups': [Group.objects.get(name='admin'), Or, 'client']
```

- Permissions takes DRF permissions(class based), Django permission objects and Django permission names(codenames), so you can use those operators however you want with these three, you can even use all three types together, e.g
```py
'permissions': [IsAuthenticated, And, Permissions.objects.get('view_user'), Or, 'change_user']
```

### Note:
- `And`, `Or` & `Not` are the equvalent operators for `and`, `or` & `not` respectively 
- Unlike `and`, `or` & `not` the operators `And`, `Or` & `Not` have no precedence they are evaluated from left to right, if you want precedence use list or tuple to make one i.e `[IsAuthenticated, And, [IsAdmin, Or, IsClient]]`
- The `'__all__'` on groups stands for any group(or allow all groups)
- The GET-list stands for permission & groups in `GET: /users/` route
- The GET-retrieve stands for groups & permissions in `GET: /users/{id}/` routes
- The POST stands for groups & permissions in `POST: /users/` route
- The PUT stands for groups & permissions in `PUT: /users/{id}/` routes
- The PATCH stands for groups & permissions in `PATCH: /users/{id}/` routes
- The DELETE stands for groups & permissions in `DELETE: /users/{id}/` routes

