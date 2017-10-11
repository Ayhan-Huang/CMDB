/**
 * Created by aibuz on 2017/10/11.
 */

String.prototype.format = function (args) {
    return this.replace(/\{(\w+)\}/g, function (s, i) {
        return args[i];
    });
};

//页面加载之后AJAX从/server/server_json/请求数据，渲染页面
$(function () {
    init();
});

function init() {
    $('#loading').removeClass('hide'); //去除loading模态框隐藏

    $.ajax({
        url: '/server_json.html',
        type: 'GET',
        data: {},
        dataType: 'JSON',
        success: function (response) {
            console.log(response.table_config);
            console.log(response.data_list);
            initTableHead(response.table_config);
            initTableBody(response.table_config, response.data_list);
            // 去除loading效果
            $('#loading').addClass('hide');
        },
        error: function () {
            // 去除loading效果
            $('#loading').addClass('hide');
        }
    })
}

// 填充表头
function initTableHead(table_config) {
    $('#tableThead').children("tr").empty();  //因为如果再次调用init()那么会导致表头重复添加，因此，每次都执行清空表头
    $.each(table_config, function (index, conf) {
        var th = document.createElement('th');
        th.innerHTML = conf.title;
        console.log(conf.title);
        console.log(th);
        $('#tableThead').children('tr').append(th);
    })
}

//填充表数据
function initTableBody(table_config, data_list) {
    /*
     data_list = [
     {'hostname': xxx, 'sn': xxx, 'os": xxx}  --> row_dict
     ]
     */
    $.each(data_list, function (index, row_dict) {
        var tr = document.createElement('tr');

        $.each(table_config, function (index, dict) {
            var td = document.createElement('td');
            /* dict:
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
             */
            //td.innerHTML = row_dict[dict.q]; // 记录：None, id, hostname, sn, os_platform...
            //undefined	2	c1.com	Parallels-1A 1B CB 3B 64 66 4B 13 86 B0 86 FF 7E 2B 20 30	linux	CentOS release 6.6 (Final) Kernel on an \m	运维	undefined
            var format_dict = {};
            $.each(dict.text.kwargs, function (k, v) {
                if (v[0] == '@') {   //定义，如果是以@开头，那么就表示格式化tpl时，用@后面的字段查询数据库的结果；否则，直接用字符串格式化
                    var name = v.substring(1);
                    console.log('name is ' + name);
                    format_dict[k] = row_dict[name]
                } else {
                    format_dict[k] = v;
                }
            });

            td.innerHTML = dict.text.tpl.format(format_dict);

            $(tr).append(td); // jQuery直接包dom对象
        });

        $('#tableBody').append(tr);
    })
}
