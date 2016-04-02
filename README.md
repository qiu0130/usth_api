# 黑科技成绩查询API

> usthAPI

### Get
 
[http://www.usth.applinzi.com](http://www.usth.applinzi.com) (json)

### 说明
+ 不及格成绩
```
{
status: "ok",
尚不及格成绩: [ ],
_id: "2013025305",
create_time: "2016-04-02 09:34:12",
曾不及格成绩: []
}
```

+ 本学期成绩

```
{
status: "ok",
_id: "2013025305",
create_time: "2016-04-02 10:35:44",
本学期成绩: []
}
```

+ 全部及格成绩

```
{
status: "ok",
_id: "2013025305",
create_time: "2016-04-02 10:36:21",
全部及格成绩: {}
}
```

+ 出错

```
{
error: "您的密码不正确，请您重新输入！"
}
```

### 其他
The MIT License

