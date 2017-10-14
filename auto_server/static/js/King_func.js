/**
 * Created by aibuz on 2017/10/11.
 */

//利用自执行函数 和 定义jQuery扩展(不让init()立即执行）

(function (jq) {

    var requestUrl = "";
    var GLOBAL_CHOICES_DICT = {};

    //定义原型，令所有的String对象都有format方法
    String.prototype.format = function (args) {
        return this.replace(/\{(\w+)\}/g, function (s, i) {
            return args[i];
        });
    };

    function init(pageNum) {
        $('#loading').removeClass('hide'); //去除loading模态框隐藏

        var searchConditions = getSearchConditions();

        //页面加载之后AJAX从/server_json.html请求数据，渲染页面
        $.ajax({
            url: requestUrl,
            type: 'GET',
            data: {'pageNum': pageNum, 'searchConditions': JSON.stringify(searchConditions)},
            //AJAX发送data ,不支持key的值是列表或字典，如果是列表，加参数traditional: true；如果是字典，要序列化为字符串
            dataType: 'JSON',
            success: function (response) {
                initGCD(response.global_choices_dict);
                initTableHead(response.table_config);
                initTableBody(response.table_config, response.data_list);
                initPagination(response.page_html);
                initSearch(response.search_config);
                bindSearchEvent();
                // 去除loading效果
                $('#loading').addClass('hide');
            },
            error: function () {
                // 去除loading效果
                $('#loading').addClass('hide');
            }
        })
    }

    //初始化GLOBAL_CHOICES_DICT
    function initGCD(global_choices_dict) {
        GLOBAL_CHOICES_DICT = global_choices_dict;
    }

    // 填充表头
    function initTableHead(table_config) {
        $('#tableThead').children("tr").empty();  //因为如果再次调用init()那么会导致表头重复添加，因此，每次都执行清空表头
        $.each(table_config, function (index, conf) {
            if (conf.display) { //决定是否显示
                var th = document.createElement('th');
                th.innerHTML = conf.title;
                $('#tableThead').children('tr').append(th);
            }
        })
    }

    //填充表数据
    function initTableBody(table_config, data_list) {
        $('#tableBody').empty(); //清空数据，否则点击翻页内容会叠加
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
                        if (v.substring(0, 2) === '@@') { //定义：@@，则从静态字段中取出对应的状态说明
                            var name = v.substring(2);  // name=server_status
                            var status_code = row_dict[name];  //status_code=1
                            var server_status_code_list = GLOBAL_CHOICES_DICT.server_status_code;
                            $.each(server_status_code_list, function (index, list) {
                                if (list[0] === status_code) {
                                    format_dict[k] = list[1];
                                    return false;
                                }
                            })
                        } else if (v[0] === '@') {   //定义，如果是以@开头，那么就表示格式化tpl时，用@后面的字段查询数据库的结果；否则，直接用字符串格式化
                            var name = v.substring(1);
                            format_dict[k] = row_dict[name]
                        } else {
                            format_dict[k] = v;
                        }
                    });

                    td.innerHTML = dict.text.tpl.format(format_dict);

                    //为td增加属性
                    $.each(dict.attr, function (attr, val) {
                        if (val[0] === '@') {
                            var name = val.substring(1);
                            val = row_dict[name];
                        }
                        td.setAttribute(attr, val);
                    });

                    $(tr).append(td); // jQuery直接包dom对象
                }
            });

            $('#tableBody').append(tr);
        })
    }

    //初始化分页
    function initPagination(page_html) {
        //清空页面的分页内容，重新添加分页
        $('#pagination').empty().append(page_html);

        //为页码a标签绑定事件,这个事件执行jQuery扩展方法：
        // 因为代码被封装在自执行函数体内，通过jQuery扩展才能访问到
        /*
        $('#pagination').on('click', 'a', function () {
            var pageNum = $(this).attr("num");
            $.changePage(pageNum);
        })
        */
    }

    //初始化搜索
    function initSearch(search_config) {
        /*
         1. 初始化搜索条件显示和默认搜索输入框类型
         2. 添加搜索条件下拉选项（即页面中bootstrap的dropdown-menu元素）：
         循环search_config：创建dropdown-menu下拉元素
         每一项的title 作为dropdown-menu的label, li-a标签的显示
         每一项的type 作为dropdown-menu的li-a标签的属性 --> 决定后面搜索框是input / select
         每一项的name 作为input/select搜索框的name属性

         如果希望翻页后，仍然保留搜索条件，那么初始化搜索只执行一次：
         1. 执行完初始化搜索后，为标签自定义布尔值属性，
         2. 再次执行初始化搜索时，先判断布尔值，为true，不执行
         */
        if (!$('#searchCondition').attr('init')) {
            console.log('执行了初始化搜索');
            initDefaultSearchCondition(search_config[0]);

            var $ulEle = $('#searchCondition').find('ul.dropdown-menu');
            $ulEle.empty(); //避免翻页造成搜索区域重复添加

            $.each(search_config, function (i, item) {
                var liEle = document.createElement('li');
                var aEle = document.createElement('a'); //用到bootstrap的组件，如果不内嵌a标签，显示效果很丑

                aEle.innerHTML = item.title;
                aEle.setAttribute('name', item.name);
                aEle.setAttribute('type', item.type);
                if (item.type == 'select') {
                    aEle.setAttribute('choice_name', item.choice_name);
                }

                $(liEle).append(aEle);
                $ulEle.append(liEle);
            });

            //标签自定义布尔值属性
            $('#searchCondition').attr('init', true);
        }
    }

    //初始化搜索条件label显示和默认搜索输入框类型
    function initDefaultSearchCondition(item) {
        /* search_config:
         {'name': 'hostname__contains', 'title': '主机名', 'type': 'input'},
         ...
         {'name': 'server_status', 'title': '状态', 'type': 'select', 'choice_name': 'server_status_code'},
         用search_config的第一项，作lable标签显示，以及创建搜索框类型：input/select
         */
        if (item.type == 'input') {
            var ele = document.createElement('input');
            ele.setAttribute('name', item.name);
            ele.className = "form-control no-radius"; //增加bootstrap样式
            ele.setAttribute('placeholder', '请输入搜索条件，多个条件以逗号分割');
        } else {
            var ele = document.createElement('select');
            ele.setAttribute('name', item.name);
            ele.className = "form-control no-radius";
            var server_status_code = GLOBAL_CHOICES_DICT[item.choice_name];
            /* server_status_code = [
             [1, '上架'],
             [2, '上线'],
             [3, '离线'],
             [4, '下架'],
             ] json后元组变为列表
             */
            //创建下拉选项
            $.each(server_status_code, function (i, list) {
                var optEle = document.createElement('option');
                optEle.innerText = list[1];
                optEle.setAttribute('value', list[0]);

                $(ele).append(optEle);
            })
        }
        //label显示初始值
        $('#searchCondition').find('label').text(item.title);
        //添加默认搜索输入框
        $('#searchCondition').find('.input-group').append(ele);

        //注意，不要用$对象调用DOM对象的方法；除非$_obj[0]拿到DOM对象
    }

    //绑定搜索相关的事件
    function bindSearchEvent() {
        console.log('执行了搜索相关绑定');
        //点击dropdown-menu，更改label显示 以及 重建输入框(根据下拉选项类型决定重建类型input/select)
        $('#searchCondition').on('click', 'li', function () {
            //修改label显示, 通过相对定位，否则搜索条件多了会找错
            $(this).parent().prev().prev().text($(this).text());

            //删除旧的输入框，准备重建
            $(this).parent().parent().next().remove();

            var aEle = $(this).children();
            var name = aEle.attr('name');
            var title = aEle.text();
            var type = aEle.attr('type');

            if (type == 'input') {
                var ele = document.createElement('input');
                ele.setAttribute('placeholder', '请输入搜索条件，多个条件以逗号分割');
            } else {
                //select
                var ele = document.createElement('select');
                var choice_name = aEle.attr('choice_name');
                var server_status_code = GLOBAL_CHOICES_DICT[choice_name];
                /* server_status_code = [
                 [1, '上架'],
                 [2, '上线'],
                 [3, '离线'],
                 [4, '下架'],
                 ] json后元组变为列表
                 */
                //创建下拉选项
                $.each(server_status_code, function (i, list) {
                    var optEle = document.createElement('option');
                    optEle.innerText = list[1];
                    optEle.setAttribute('value', list[0]);

                    $(ele).append(optEle);
                })
            }
            ele.setAttribute('name', name);
            ele.className = "form-control no-radius"; //增加bootstrap样式

            //添加搜索框,通过相对定位，否则搜索条件多了会找错
            $(this).parent().parent().parent().append(ele);


        });

        //新增搜索条件
        $('.add-condition').click(function () {
            var $newCondition = $(this).parent().parent().clone();
            $newCondition.find('.add-condition').removeClass('add-condition').addClass('del-condition');
            $newCondition.find('.fa-plus-square').attr('class','fa fa-minus-square');
            $('#searchCondition').append($newCondition);
        });

        //删除搜索条件
        $('#searchCondition').on('click', '.del-condition', function () {
            $(this).parent().parent().remove();
        });

        //点击搜索按钮
        $('#doSearch').click(function () {
            //点击搜索，将搜索条件发送给server, 还要走init，因此；直接在init中执行一个函数获取搜索条件，发送给服务端
           init(1);
        })

    }

    //获取搜索条件，处理成字典形式
    function getSearchConditions() {
        var searchConditions = {};
        var $resultSET = $('#searchCondition').find('input,select'); //find()方法可以在一对儿引号内加入多个条件

        $.each($resultSET, function () {
            var name = $(this).attr('name');
            var val = $(this).val(); //select元素也可以用val取值
            if (searchConditions[name]) {
                searchConditions[name].push(val);
            } else {
                searchConditions[name] = [val];
            }
        });
        console.log(searchConditions);
        return searchConditions;
    }

    //通过jQuery扩展暴露一个调用接口
    jq.extend({
        'King_func': function (url) {
            requestUrl = url;
            init(1);
        },

        'changePage': function (pageNum) {
            init(pageNum);
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

