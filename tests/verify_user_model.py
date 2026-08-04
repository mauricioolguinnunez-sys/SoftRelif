import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.preference_model import PreferenceModel
from models.user_model import UserModel
import json

print('get_account_settings:', json.dumps(UserModel.get_account_settings(1), ensure_ascii=False, default=str))
print('update_account_settings:', json.dumps(UserModel.update_account_settings(1, 'Especialista SoftRelief', 'especialista', 'especialista@softrelief.com'), ensure_ascii=False, default=str))
print('update_password:', json.dumps(UserModel.update_password(1, 'especialista123', 'especialista123', 'especialista123'), ensure_ascii=False, default=str))
print('update_theme:', json.dumps(PreferenceModel.update_theme(1, 'dark'), ensure_ascii=False, default=str))
