# drf-guard

Create flexible and simple to use access rules for Django REST Framework(DRF). Works with both class based DRF permissions, Django permissions and Django groups. This library allows you to build complex access rules in a very simple way, it allows you to combine permissions and groups with logical operators.

Have you ever had multiple permissions or groups and wanted to be able to do something like below to your endpoint?.
```py
# Check if user has certain permissions with `and`, `or` & `not` operators
permissions: (IsAdmin Or (IsObjectOwner And IsAllowedToEdit))
```

Or

```py
# Evaluate if user in certain groups with `and`, `or` & `not` operators
groups: ('admin' Or 'client' And Not 'seller')
```

Well you are not alone, this library allows you to do that with `And`, `Or` & `Not` operators to each endpoint however you want regardless whether you are using class based DRF permissions, Django permissions or Django grops, it can deal with all those.

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
    
    # Now define access rules for your API endpoint with groups and permissions as you wish
    access_rules = {
         'GET': {
             'list': {
                 # To access this the user must belongs to admin or client group
                 'groups': ['admin', Or, 'client'],
                 'permissions': [IsAuthenticated]  # Also the user must be authenticated
             },
             'retrieve': {
                 'groups': [Not, 'admin'],  # The user must not be in admin group
                 'permissions': [IsAuthenticated, And, IsAllowedUser]  # Must be authenticated and allowed
             },
         },

         'POST': {
             'groups': [],  # Don't allow at all(This evaluates to False always)
             'permissions': []  # Don't allow at all(This evaluates to False always)
         },

         'PUT': {
             'groups': '__any__',  # Belongs to any group or none
             'permissions': '__any__'  # Has any permission or none
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
- The `'__any__'` on groups/permissions stands for any group/permission or none
- The GET-list stands for permission & groups in `GET: /users/` route
- The GET-retrieve stands for groups & permissions in `GET: /users/{id}/` routes
- The POST stands for groups & permissions in `POST: /users/` route
- The PUT stands for groups & permissions in `PUT: /users/{id}/` routes
- The PATCH stands for groups & permissions in `PATCH: /users/{id}/` routes
- The DELETE stands for groups & permissions in `DELETE: /users/{id}/` routes
