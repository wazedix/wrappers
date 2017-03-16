对单实例部署程序的一些封装
=============

## Useage

见 demo.py


## 文档

* cache/memory.py
一个简易的内存缓存实现，支持基础的 set, get, delete 操作。

* cache/redis.py
支持连接多个 redis 实例，多写多读保证可用性，适合对数据一致性及性能要求不高情况下的高可用场景。
