#!/usr/bin/env python3
import futu as ft
from futu import RET_OK, Market

ctx = ft.OpenHKTradeContext(host='127.0.0.1', port=11112)
print("Connected!")

# 获取账户列表
ret, acc_list = ctx.get_acc_list()
print(f"账户列表：{ret}")
if ret == RET_OK:
    print(acc_list.to_dict())

# 尝试调用 position_list_query
import inspect
sig = inspect.signature(ctx.position_list_query)
print(f"\nposition_list_query 参数：{sig}")

ctx.close()
