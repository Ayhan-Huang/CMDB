"""
使用方法：

from utils.page import Pagination
def users(request):
    current_page = int(request.GET.get('page',1))

    total_item_count = models.UserInfo.objects.all().count()

    page_obj = Pagination(current_page,total_item_count,'/users.html')

    user_list = models.UserInfo.objects.all()[page_obj.start:page_obj.end]

    return render(request,'users.html',{'user_list':user_list,'page_html':page_obj.page_html()})


"""


from django.utils.safestring import mark_safe


class Pagination(object):

    def __init__(self,current_page,total_item_count,base_url=None,per_page_count=10,show_pager_count=11):
        """
        :param current_page:  当前页
        :param total_item_count: 数据库数据总条数
        :param base_url: 分页前缀URL
        :param per_page_count:   每页显示数据条数
        :param show_pager_count: 对多显示的页码
        """
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        self.current_page = current_page
        self.total_item_count = total_item_count
        self.base_url = base_url
        self.per_page_count = per_page_count
        self.show_pager_count = show_pager_count

        max_pager_num, b = divmod(total_item_count, per_page_count)
        if b:
            max_pager_num += 1
        self.max_pager_num = max_pager_num

    @property
    def start(self):
        """

        :return:
        """
        return (self.current_page-1)* self.per_page_count

    @property
    def end(self):
        """

        :return:
        """
        return self.current_page * self.per_page_count

    def page_html(self):
        """
        给模板用，后台渲染页面
        :return:
        """
        page_list = []

        if self.current_page == 1:
            prev = ' <li><a href="#">上一页</a></li>'
        else:
            prev = ' <li><a href="%s?page=%s">上一页</a></li>' % (self.base_url,self.current_page - 1,)
        page_list.append(prev)

        half_show_pager_count = int(self.show_pager_count / 2)

        # 数据特别少，15条数据=2页
        if self.max_pager_num < self.show_pager_count:
            # 页码小于11
            pager_start = 1
            pager_end = self.max_pager_num + 1
        else:
            if self.current_page <= half_show_pager_count:
                pager_start = 1
                pager_end = self.show_pager_count + 1
            else:
                if self.current_page + half_show_pager_count > self.max_pager_num:
                    pager_start = self.max_pager_num - self.show_pager_count + 1
                    pager_end = self.max_pager_num + 1
                else:
                    pager_start = self.current_page - half_show_pager_count
                    pager_end = self.current_page + half_show_pager_count + 1

        for i in range(pager_start, pager_end):
            if i == self.current_page:
                tpl = ' <li class="active"><a href="%s?page=%s">%s</a></li>' % (self.base_url,i, i,)
            else:
                tpl = ' <li><a href="%s?page=%s">%s</a></li>' % (self.base_url,i, i,)
            page_list.append(tpl)

        if self.current_page == self.max_pager_num:
            nex = ' <li><a href="#">下一页</a></li>'
        else:
            nex = ' <li><a href="%s?page=%s">下一页</a></li>' % (self.base_url,self.current_page + 1,)
        page_list.append(nex)

        return mark_safe(''.join(page_list))

    def page_html_js(self):
        # 给前端JS，由前端生成页码
        page_list = []

        if self.current_page == 1:
            prev = ' <li><a href="#">上一页</a></li>'
        else:
            prev = ' <li><a num="{page}">上一页</a></li>'.format(page=self.current_page-1)
            # <a num="{page}"> 将页码作为a标签的属性，前端为a标签绑定方法：拿到属性值，执行翻页
        page_list.append(prev)

        half_show_pager_count = int(self.show_pager_count / 2)

        # 数据特别少，15条数据=2页
        if self.max_pager_num < self.show_pager_count:
            # 页码小于11
            pager_start = 1
            pager_end = self.max_pager_num + 1
        else:
            if self.current_page <= half_show_pager_count:
                pager_start = 1
                pager_end = self.show_pager_count + 1
            else:
                if self.current_page + half_show_pager_count > self.max_pager_num:
                    pager_start = self.max_pager_num - self.show_pager_count + 1
                    pager_end = self.max_pager_num + 1
                else:
                    pager_start = self.current_page - half_show_pager_count
                    pager_end = self.current_page + half_show_pager_count + 1

        for i in range(pager_start, pager_end):
            if i == self.current_page:
                tpl = ' <li class="active"><a num="{page}"  >{page}</a></li>'.format(page=i)
            else:
                tpl = ' <li><a num="{page}" >{page}</a></li>'.format(page=i)
            page_list.append(tpl)

        if self.current_page == self.max_pager_num:
            nex = ' <li><a href="#">下一页</a></li>'
        else:
            nex = ' <li><a num="{page}">下一页</a></li>'.format(page=self.current_page+1)
        page_list.append(nex)

        return ''.join(page_list)
        # 因为数据不是传到模板，而是传给前端JS处理，因此不需要mark_safe