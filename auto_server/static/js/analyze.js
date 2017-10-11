/**
 * Created by aibuz on 2017/10/11.
 */
//此文件是思路展示


//定义原型，令所有的String对象都有format方法
String.prototype.format = function (args) {
    return this.replace(/\{(\w+)\}/g, function (s, i) {
        return args[i];
    });
};

$(function() {
    init();
});

function init() {
    $.ajax({
        url: '/server_json.html',
        type: 'GET',
        data: {},
        dataType: 'JSON',
        success: function (response) {
            initTableThead(response.table_config);
            //initTableBodyOld(response.table_config, response.data_list);
            initTableBodyNew(response.table_config, response.data_list);
        }
    })
}

function initTableThead(table_config) {
    /* table_config: 循环table_config拿到title，填充到页面的table表头中
    [
     {
        'q': "hostname",
        'title': '主机名',
    },
    ]
     */
    //清空表头，以免重复添加
    $.each(table_config, function(index, dict) {
        //创建表头字段，并添加到<thead><tr>下
        var th = document.createElement('th');
        th.innerHTML = (dict['title']);
        $('#tableThead').children('tr').append(th);
    })
}

function initTableBodyOld(table_config, data_list) {
    //思路分析用，正式的用initTableBodyNew

    /* data_list:
     [
     {'hostname': xxx, 'sn': xxx, 'os": xxx}  --> row_dict
     ]
     */

    $.each(data_list, function(index, row_dict) {
        //每个row_dict相当于tbody中的一行内容tr；循环row_dict字典，拿到其中字段对应的值
        var tr = document.createElement('tr');

        /*
        $.each(row_dict, function (field, value) {
            //每个value相当于tr中的一个td
            var td = document.createElement('td');
            td.innerHTML = value;
            tr.append(td);
            // 问题：row_dict是字典，对它的循环是无序的，这可能导致tbody字段值和thead表头对不上
        })
        */

        //为了解决字典循环无序的问题，这里改为循环table_config列表，其中取到的字段是有序的
        $.each(table_config, function(index, dict) {
            var td = document.createElement('td');
            td.innerHTML = row_dict[dict['q']];
            tr.append(td);
        });

        $('#tableBody').append(tr);
        //假如只是数据库字段展示，那么以上这种就可以了。

    });

    /* 但是，页面中展示的数据不止是数据库中的字段，还有选择框，编辑等选项，因此后端定制table_config为以下形式：
    [
     {
    'q': "hostname",
    'title': '主机名',
    'text': {'tpl': '{a1}', 'kwargs': {'a1': '@hostname'}},  --> 增加text, 以兼容处理数据库字段和前端展示选项
    },
    ]
    tpl 字符串模板， kwargs用于替换的内容
    我们根据这种数据结构，在下面重写initTableBodyNew来实现填充表内容
     */
}

function initTableBodyNew(table_config, data_list) {
    /* table_config = [
     {
     'q': None,
     'title': '选择',
     'text': {'tpl': '<input type="checkbox" value={id}>', 'kwargs': {'id': '@id'}},
     },
     {
     'q': 'id',
     'title': 'ID',
     'text': {'tpl': '{a1}', 'kwargs': {'a1': '@id'}},
     },
     ]

     data_list = [
     {'hostname': xxx, 'sn': xxx, 'os": xxx}  --> row_dict
     ]

     */
    $.each(data_list, function (index, row_dict) {
        var tr = document.createElement('tr');

        $.each(table_config, function (index, dict) {
            var td = document.createElement('td');

            var format_dict = {};
            $.each(dict.text.kwargs, function (k, v) {
                //定义，如果是以@开头，那么就表示格式化tpl时，用@分离的字段取数据库查询结果；否则，直接用字符串格式化
                if (v[0] === '@') {
                    var field = v.substring(1);
                    format_dict[k] = row_dict[field] //以字段的数据库查询结果作为k稍后的格式化内容
                } else {
                    format_dict[k] = v;
                }
            });
            td.innerHTML = dict.text.tpl.format(format_dict); //格式化tpl值
            $(tr).append(td); // jQuery直接包dom对象
        });
        $('#tableBody').append(tr);
    })
}


/*
以上就基本写完了，只需要在页面中引入即可：
<script src="{% static 'js/analyze.js' %}"></script>

但是可能有问题，那就是这里定义的函数和页面中要用到的其它函数可能重名，为了避免这种情况，需要利用函数的作用域隔离
因此，将可以将以上代码用另一个函数包起来，结果就是同目录下的Papa_func.js；并且增加了控制加载框动画效果的代码。
*/