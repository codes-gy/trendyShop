from app.lib.passport.jwtStrategy import jwt_strategy
from app.lib.passport.localStrategy import local_strategy
from app.lib.passport.roleGuard import require_admin

local_authenticate = local_strategy
jwt_authenticate = jwt_strategy
admin_authenticate = require_admin
