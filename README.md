# 家政服务预约系统

基于Django框架开发的家政服务预约平台

## 功能特点
- 用户认证系统（登录/注册）
- 服务展示与预约功能
- 订单管理系统
- 响应式网页设计

## 系统要求
- Python 3.8+
- MySQL 5.7+
- 完整依赖请查看[requirements.txt](requirements.txt)

## 安装指南
1. 克隆项目仓库
2. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   source venv/Scripts/activate  
   ```
3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
4. 在`home_service_booking/settings.py`中配置数据库
5. 执行数据库迁移：
   ```bash
   python manage.py migrate
   ```
6. 创建管理员账户：
   ```bash
   python manage.py createsuperuser
   ```
7. 启动开发服务器：
   ```bash
   python manage.py runserver
   ```

## 配置说明
复制`.env.example`为`.env`并设置环境变量：
```
SECRET_KEY=你的密钥
DB_NAME=数据库名
DB_USER=数据库用户
DB_PASSWORD=数据库密码
```

## 许可证
MIT开源协议
