/**
 * Created by aibuz on 2017/10/11.
 */

//利用自执行函数 和 定义jQuery扩展(不让init()立即执行）

(function (jq) {

    var requestUrl = "";

    //定义原型，令所有的String对象都有format方法
    String.prototype.format = function (args) {
        return this.replace(/\{(\w+)\}/g, function (s, i) {
            return args[i];
        });
    };

    function init() {
        $('#loading').removeClass('hide'); //去除loading模态框隐藏

        //页面加载之后AJAX从/server_json.html请求数据，渲染页面
        $.ajax({
            url: requestUrl,
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
            if (conf.display) {
                var th = document.createElement('th');
                th.innerHTML = conf.title;
                console.log(conf.title);
                console.log(th);
                $('#tableThead').children('tr').append(th);
            }
        })
    }

    //填充表数据
    function initTableBody(table_config, data_list) {
        /*
         data_list = [
         {'hostname': xxx, 'sn': xxx, 'os": xxx}  --> row_dict
         ]
         */
        $.each(data_list, function (index, row_dict) {  //第一层循环数据，每一行数据就是table显示的一个tr
            var tr = document.createElement('tr');

            $.each(table_config, function (index, dict) { //第二层有序循环
                if (dict.display) {
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
                    $.each(dict.text.kwargs, function (k, v) { //第三层兼容前端选项和数据库字段显示  --> 字符串格式化
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
                }
            });

            $('#tableBody').append(tr);
        })
    }

    jq.extend({
        'King_func': function (url) {
            requestUrl = url;
            init();
        }
    });

})(jQuery);

/*
 1.自执行函数：实现了作用域的绝对隔离和函数名的冲突问题；
 2.定义jQuery扩展：拿到函数调用和执行的主动权。
 3.将ajax请求的url改为传参的方式，实现可复用。
 */


/*
 使用：
 <script src="{% static 'js/King_func.js' %}"></script>
 <script>
 $.King_func('/server_json.html');
 </script>
 */


/************************************************************************
 //自执行函数（匿名函数用括号包起来），函数无名子，加括号传参会立即执行
 (function (args) {
    alert(args)
})(666);

 //如果不需要立即执行的特性，利用jQuery扩展特性，为jQuery定义一个方法，调用该方法才执行
 方式一：
 jQuery.extend({
    'myMethod': function (args) {
        alert(args)
    }
});

 $.myMethod(777); //调用自定义方法


 方式二：
 //定义
 jQuery.fn.extend({
    'myMethod': function(args) {
        alert(args);
    }
});

 //通过选择器调用
 $(seletor).myMethod(args);


 ****************************************************************************/


/* 其它说明：
 <script src="{% static 'plugins/jquery-3.2.1.js' %}"></script>
 在页面中引入jQuery之后，该对象全局可用
 $ 和 jQuery 是一样的

 //匿名函数，比如：
 ajax: success: function() {}
 setInterval(function() {}, 1000)

 */


/*
 kwargs = {
 'a': 'A',
 'b': 'B',
 };


 String.prototype.format = function(kwargs) {
 return this.replace(/\{\w+}/g, function(k, v) {
 //RE匹配时，K匹配花括号，v匹配花括号内容
 return kwargs[k];
 })
 };

 var name = 'aabb';
 name.format(kwargs);
 */

