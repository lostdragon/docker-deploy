## 接口规范
### 网址
#### 开发：

- C端接口：http://api.iweshi.com:8000/v1 (正式)
- C端接口：http://api.zmei.me:8000/v1 (暂用)


#### 正式：

- C端接口：http://api.iweshi.com/v1 (正式)
- C端接口：http://api.zmei.me/v1 (暂用)

### 客户端
即**client_id**的定义：

- 13 后台web端
- 23 收银web端
- 31 B端android
- 32 B端ios
- 41 C端Android
- 42 C端iOS
- 44 爱美兔微信端
- 53 C端后台Web端

## 接口
### 变更历史

### 2015.7.28 - 
- 增加微信帐号绑定和登录
- 测试记录支持新B端美艺人生美发师
- 广告条增加位置字段

### 2015.6.28 - 2015.7.27
- 更新样品接口
- 更新订单接口
- 增加订单数量接口

### 2015.6.10 - 2015.6.27
- 增加样品接口
- 增加试用接口
- 增加订单支付接口
- 更新测试记录接口
- 增加绑卡二维码接口

### 2015.6.3 - 2015.6.9
- 产品列表增加库存字段
- 订单产品增加品牌和规格
- 产品列表图片改为对象形式

### 2015.5.25 - 2015.6.2
- 产品功效改为字符串
- 产品品牌描述改为图文混排
- 增加广告条接口
- 增加专题接口
- 更新产品排序
- 增加获取多个产品接口

#### 2015.5.18-2015.5.22
- 增加产品上下架状态、品牌、规格、保质期、产地、服务
- 推荐产品根据总星级排序
- 增加获取最近一次测试详情接口
- 测试详情增加测试是否完成字段status
- 头皮测试增加问卷类型 SHOP 和 USER
- C端用户提交测试问卷
- 测试结果增加类型、护理建议
- 获取健康发质设置

### 登录接口
#### 错误业务代码

- (1001, '验证码错误次数超过限制', error='SMS.ErrorCountLimited')
- (1002, '验证码过期', error='SMS.Timeout')
- (1003, '验证码已经验证过', error='SMS.Checked')
- (1004, '无效验证码', error='SMS.Invalid')
- (1005, '错误验证码', error='SMS.Incorrect')
- (1006, '验证码请求太频繁', error='SMS.TooOften')

- (1010, '帐号不存在', error='Account.NotFound')
- (1011, '帐号密码错误')
- (1012, '密码修改失败')
- (1013, '手机号格式错误', error='Mobile.Incorrect')
- (1014, '手机号已占用', error='Account.MobileExist')

#### 登陆获取手机验证码(完成)
- POST /login/sms_code
- 参数

        {
            "is_voice": "1语音，0短信,int",
            "is_try": "1重试，0首次,int",
            "mobile": "手机号（格式: 13333333333）,string"
        }

#### 手机验证码登陆(完成)
- POST /login/token
- 参数
        
        // 注册、手机号码登录、忘记密码、绑定微信帐号
        {
            "grant_type": "sms_code",  // 固定值
            "mobile": "手机号（格式: 13333333333）,string",
            "sms_code": "手机校验码,string",
            "client_id": "客户端ID,int",
            "password": "密码,string,需长度>=6,可选",
            "nickname": "昵称,string,可选,微信昵称，只有用户昵称为空时才能设置成功",
            "openid": "微信openid,string,可选，绑定微信帐号时需要传此参数",
            "avatar_url": "头像URL,string,可选,微信头像，只有用户头像为空时才能设置成功"
            "gender": "性别,可选，0未知，1男，2女"
        }
        
        // 密码登录
        {
            "grant_type": "password",  // 固定值
            "mobile": "手机号（格式: 13333333333）,string",
            "password": "密码,需长度>=6,string",
            "client_id": "客户端ID,int"
        }
        
        // 微信openid登录
        {
            "grant_type": "openid",  // 固定值
            "openid": "微信openid,string",
            "client_id": "客户端ID,int"
        }

- 返回

        {
            "access_token": "授权字符串",
            "expires_in": "过期时长"
        }

#### 注销(完成)
- DELETE /login/token

### 帐号接口
#### 获取账号信息(完成)
- GET /accounts/me
- 返回

        {
            "id": "ID,bigint",
            "mobile": "手机,string",
            "password_is_ok": "0需要修改，1不需要修改,int",
            "nickname": "昵称,string",
            "avatar": {"src": "图片源,string", "url": "图片URL,string"},
            "gender": "性别,int,0 未知, 1 男, 2 女",
            "point": "积分，int",
            "is_testing": "是否测试过，int, 0否，1是",
            "openid": "微信openid,string"
            "location": {
                "province":{
                    "id": "省ID,int",
                    "name": "省名称,string"
                },
                "city": {
                    "id": "市ID,int",
                    "name": "市名称,string"
                }
            }
        }

#### 修改账号信息(完成)
- PUT /accounts/me
- 返回

        {
            "nickname": "昵称,string",
            "avatar": "头像src,string",
            "gender": "性别,int,0 未知, 1 男, 2 女",
            "province_id": "省ID,int",
            "city_id": "市ID,int"
        }

#### 修改密码(完成)
- PUT /accounts/me/password
- 参数

        {
            "proof_state": "password_is_ok", //因为弱密码需要重置密码
            "value": "新密码"
        }
        or
        {
            "proof_state": "password", //修改密码
            "password": "旧密码",
            "value": "新密码"
        }

#### 获取已测试的门店列表(完成)
- GET /accounts/me/shops
- 返回
    
        [
            {
                
                "brand": {
                    "founder_name": "创建者名称,string",
                    "id": "品牌ID,bigint",
                    "name": "品牌名称,string"
                },
                "id": "门店ID,int",
                "name": "店名,string",
                "street": "具体地址,string",
                "contact_tel": "联系电话,string",
                "is_exp": "是否体验店,int, 0否 1是",
            }       
        ]

#### 获取积分变更历史(完成)
- GET /accounts/me/points
- 返回
    
        [
            {
                "create_time": "创建时间戳,int",
                "event_id": "事件ID,int",
                "event_type": "事件类型，string,包含TRIAL,REGISTER,COMMENT",
                "id": "历史ID,int",
                "point": "积分变更,int，> 0 为增加积分, < 0 为减少积分",
                "reason": "变更原因,string",
                "user_id": "用户ID"
            }
        ]
        