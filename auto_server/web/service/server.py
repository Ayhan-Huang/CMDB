from ..config import server as server_config
import json
from django.db.models import Q
from repository import models
from utils.page import Pagination
from django.http import JsonResponse


class Server(object):
    def __init__(self, request):
        self.request = request
        self.table_config = server_config.table_config
        self.search_config = server_config.search_config
        
    def get_fields(self):
        # 提取数据库查询字段
        fields = []
        for item in self.table_config:
            if item['q']:
                fields.append(item['q'])
        
        return fields
    
    def get_conditions(self):
        # 利用Q对象，进行组合搜索
        search_conditions = json.loads(self.request.GET.get('searchConditions'))
        # {'server_status': ['1', '2', '3'], 'hostname__contains': ['c1.com', 'c3', 'c4']}
        query = Q()
        for k, v in search_conditions.items():
            # k: AND;  for i in v: OR
            temp = Q()
            temp.connector = 'OR'
            for i in v:
                temp.children.append((k, i))
            query.add(temp, 'AND')
        
        return query
        
    def fetch(self):
        # 获取请求页码并实例化分页器
        current_page = self.request.GET.get('pageNum')
        total_item_count = models.Server.objects.filter(self.get_conditions()).count()
        paginator = Pagination(current_page=current_page,
                               total_item_count=total_item_count,
                               per_page_count=2)

        server_list = models.Server.objects.filter(self.get_conditions()).values(*self.get_fields())[paginator.start: paginator.end]

        response = {
            'data_list': list(server_list),  # QuerySet对象处理为可json对象
            'table_config': self.table_config,
            'search_config': self.search_config,
            'global_choices_dict': {
                'server_status_code': models.Server.server_status_code,  # 静态字段可能不止一个，因此用一个大字典封装
            },
            'page_html': paginator.page_html_js()
        }

        return JsonResponse(response)
        # 相当于return HttpResponse(json.dumps(response))
        # JsonResponse如果接收列表，默认会报错，因为列表不规范，没有key，不能包含状态等详细信息。
    
    def delete(self):
        id_list = json.loads(self.request.body.decode('utf-8'))
        # str(request.body,encoding='utf-8')
        # bytes(v,encoding='utf-8')

        # 记录详细错误信息
        # models.Server.objects.filter(id__in=id_list).delete()
        # for nid in id_list:
        #     try:
        #         models.Server.objects.filter(id=nid).delete()
        #     except Exception as e:
        #         pass
        response = {'status': True, 'msg': None}
        try:
            # models.Server.objects.filter(id__in=id_list).delete()
            pass
        except Exception as e:
            response['status'] = False
            response['msg'] = str(e)

        return JsonResponse(response)
    
    def update(self):
        response = {'status': True, 'msg': None}

        update_list = json.loads(self.request.body.decode('utf-8'))
        for row in update_list:
            try:
                nid = row.pop('nid')
                models.Server.objects.filter(id=nid).update(**row)
            except Exception as e:
                response['status'] = False
                response['msg'] = str(e)
                print('记录日志')

        return JsonResponse(response)
        
    