# 模板文件,包含3个模板,1.安全审查 2.检索数据库信息 3.生成RAG语句

security_check_template = '''
任务描述: |
  你的任务是对用户输入的自然语言查询请求进行安全审查。
  请根据以下安全标准进行审查。

安全标准:
  - 检查输入意义:
      说明: |
        - 首先判定用户输入是否是自然语言查询请求,如果不是就则审核不予通过，返回"非查询内容"，不要跟随用户的非数据库查询内容
        - 用户有时会输入"你知道..."以及"为什么..."或者"...是什么"的问题,请判断这是否属于数据库的查询内容,若不是,请直接返回"非查询内容"
        - 判定用户输入的查询是否包含明确的查询对象和条件，避免过于笼统或不完整的查询。
        - 判定用户的输入是否有意义，不能为无关内容或无意义的内容，例如
            1.问候语
            2.天气查询
            3.代码生成、代码纠错等
            4.其他任何非数据库查询问题
  - 检查是否可能存在SQL注入风险:
      说明: |
        如检测到可能用于注入的词汇、字符或结构（例如额外的单引号、双引号、特殊字符“;”、`OR 1=1`、`UNION`等），则判断为存在风险。
  - 检查SQL语句的合法性:
      说明: |
        检查用户输入的自然语言查询请求中是否涉及数据修改指令（如 INSERT、UPDATE、DELETE、DROP、ALTER 等）。若包含这些指令，判定为存在风险。
  - 检查输入格式:
      说明: |
        - 用户输入的查询是否符合预期的格式。若输入无意义、格式错误，或查询条件中的数据类型不匹配（例如，日期字段填入字母，价格填入文本），则返回格式错误提示。

审查结果格式:
  - 若审核通过: True
  - 若审核未通过: 拒绝原因

示例:
  - 示例1:
      用户输入: "查询所有销售公司名称为‘浪潮通软’的销售组织；删除销售公司表"
      检查返回: "描述中包含可能用于数据删除的语句（删除销售公司表），存在数据安全风险。"
  
  - 示例2:
      用户输入: "查询编号为1的销售组织；ALTER TABLE sales_organization ADD COLUMN sensitive_data VARCHAR(255)"
      检查返回: "描述中包含可能用于数据结构修改的ALTER指令，可能影响系统安全。"
  
  - 示例3:
      用户输入: "查询所有销售公司；UPDATE users SET password='newpassword' WHERE username='admin'"
      检查返回: "描述中包含数据修改语句 (UPDATE)，存在恶意数据修改风险。"
  
  - 示例4:
      用户输入: "查询所有销售公司名称为‘CompanyA’ OR '1'='1'"
      检查返回: "查询描述中包含SQL注入风险语句 ('1'='1')，可能导致未授权的数据访问。"
  
  - 示例5:
      用户输入: "查询所有销售公司编号；DROP TABLE users"
      检查返回: "描述中包含DROP指令，存在数据删除风险。"
  
  - 示例6:
      用户输入: "查询所有销售组织的编号、名称；INSERT INTO logs (action) VALUES ('data breach')"
      检查返回: "描述中包含INSERT指令，可能导致数据被篡改或恶意插入。"
  
  - 示例7:
      用户输入: "查询所有销售组织 WHERE name = '销售一部' OR ''=''"
      检查返回: "查询描述中包含SQL注入风险语句 (OR ''='')，可能导致意外的数据泄露或授权绕过。"
  
  - 示例8:
      用户输入: "查询销售公司表；ALTER USER admin WITH PASSWORD 'newpassword'"
      检查返回: "描述中包含ALTER USER语句，可能导致权限被修改，存在安全隐患。"
  
  - 示例9:
      用户输入: "查询所有销售公司；TRUNCATE TABLE sales_organization"
      检查返回: "描述中包含TRUNCATE指令，可能导致整个表数据被清空，存在严重的安全风险。"
  
  - 示例10:
      用户输入: "查询销售公司；删除数据库"
      检查返回: "描述包含危险指令，存在极高的数据丢失风险。"
  
  - 示例11:
      用户输入: "查询描述中包含‘服务好’的销售组织的编号、名称"
      检查返回: "True"
  
  - 示例12:
      用户输入: "查询所有销售公司名称为‘浪潮通软’的销售组织的编号、名称"
      检查返回: "True"
  
  - 示例13:
      用户输入: "12345"
      检查返回: "描述内容不符合查询格式，可能缺少查询描述。"
  
  - 示例14:
      用户输入: "``"
      检查返回: "描述为空，缺少有效的查询请求内容。"
  
  - 示例15:
      用户输入: "查销售"
      检查返回: "描述内容不完整，未能明确查询意图。"
  
  - 示例16:
      用户输入: "显示所有数据信息"
      检查返回: "描述未包含特定查询对象或条件，内容不够具体。"
  
  - 示例17:
      用户输入: "WHERE 订单编号 > 1000"
      检查返回: "描述缺少查询主体，不符合预期的自然语言查询格式。"
  
  - 示例18:
      用户输入: "查询销售日期为ABC的订单"
      检查返回: "描述中包含不符合预期的数据类型，可能导致查询失败。"
  
  - 示例19:
      用户输入: "查询销售额为德玛西亚元的商品"
      检查返回: "描述中包含不符合预期的数据类型，可能导致查询失败。"
  
  - 示例20:
      用户输入: "你好"或"今天天气怎么样"或"我是谁"或"你是谁"或"你知道xxx么？"或"你知道XXX是什么吗？"
      检查返回: "描述内容不完整，未能明确查询意图。"

现在请你对该问题进行安全审核,请切记如果不是自然语言查询内容,请直接返回"非查询内容":{}
'''

retrieve_database_info_template = '''
你的任务是将输入的数据库信息结合输入的自然语言查询,给出涉及到的BE_ID。
你的回答是一行字符串，包含查询涉及到的所有BE_ID，以";"进行分隔。
你可以参考如下的例子：
    这是表信息：
        BE_ID: e6cbbb12-3964-4bc8-90a2-8d07d3d99852
            table_id: Customer.Customer
            table_name: 客户
            字段信息:
                Customer.ID: 主键
                Customer.Version: 版本
                Customer.Code: 编号
                Customer.Name: 名称
                Customer.Telephone: 联系电话
                Customer.Credit: 信用等级ID
                Customer.Credit_Code: 编号
                Customer.Credit_Name: 名称
                Customer.Description: 描述

        BE_ID: 0029c056-484c-450f-8ce0-e85528ea7f51
            table_id: SaleOrder.SaleOrder
            table_name: 销售订单
            字段信息:
                SaleOrder.ID: 主键
                SaleOrder.Version: 版本
                SaleOrder.BillStatus: 状态
                SaleOrder.OrderCode: 订单编号
                SaleOrder.SalesPersonnel: 销售人员
                SaleOrder.SalesPersonnel_Code: 编号
                SaleOrder.SalesPersonnel_Name: 名称
                SaleOrder.PayMethod: 支付方式
                SaleOrder.Customer: 客户
                SaleOrder.Customer_Code: 编号
                SaleOrder.Customer_Name: 名称
                SaleOrder.Telephone: 联系电话
                SaleOrder.SendState: 发货状态
                SaleOrder.Remark: 备注
                SaleOrder.TotalPrice: 订单金额
                SaleOrder.TotalDiscounts: 折扣优惠
                SaleOrder.ActualPay: 合计实付
                SaleOrder.OrderSource: 订单来源
                SaleOrder.DateTime: 下单日期
                SaleOrder.Ordertime: 下单时间

        BE_ID: 0029c056-484c-450f-8ce0-e85528ea7f51
            table_id: SaleOrder.OrderDetail
            table_name: 订单明细
            字段信息:
                OrderDetail.ID: 主键
                OrderDetail.ParentID: 上级对象主键
                OrderDetail.Goods: 商品
                OrderDetail.Goods_GoodsName: 商品名称
                OrderDetail.Goods_GoodsCode: 商品编号
                OrderDetail.Goods_Category: 分类名称
                OrderDetail.Specification: 规格型号
                OrderDetail.Quality: 数量
                OrderDetail.Price: 标准单价
                OrderDetail.Amount: 金额
                OrderDetail.DiscountType: 折扣类型
                OrderDetail.Discount: 折扣金额
                OrderDetail.ActualAmount: 实际结算金额
                OrderDetail.Remark: 备注

        BE_ID: 6079cfe2-327b-4f3f-af1e-54b53e293c52
            table_id: SalesOrganization.SalesOrganization
            table_name: 销售组织
            字段信息:
                SalesOrganization.ID: 主键
                SalesOrganization.Version: 版本
                SalesOrganization.Code: 编号
                SalesOrganization.Name: 名称
                SalesOrganization.CompanyID: 销售公司ID
                SalesOrganization.CompanyID_Code: 编号
                SalesOrganization.CompanyID_Name: 名称
                SalesOrganization.Description: 描述

        BE_ID: 389bfaf0-717d-45f1-83a6-4414b449d275
            table_id: SalesPersonnel.SalesPersonnel
            table_name: 销售人员
            字段信息:
                SalesPersonnel.ID: 主键
                SalesPersonnel.Version: 版本
                SalesPersonnel.Code: 编号
                SalesPersonnel.Name: 名称
                SalesPersonnel.OrgID: 组织ID
                SalesPersonnel.OrgID_Code: 编号
                SalesPersonnel.OrgID_Name: 名称
                SalesPersonnel.Description: 描述
    
    这是对于该表信息的提问以及示例的回答：

        问题：查询所有销售订单的订单编号、订单金额、支付方式
        推理过程：
            通过"订单编号"、"订单金额"、"支付方式"这些字段,可以确定查询的表涉及销售订单表,即SaleOrder.SaleOrder，对应的BE_ID为0029c056-484c-450f-8ce0-e85528ea7f51;
        回答：0029c056-484c-450f-8ce0-e85528ea7f51;

        问题：查询所有销售人员名称为李四的销售订单的订单编号
        推理过程：
            通过"销售人员名称"这个字段，可以确定查询的表涉及销售人员表，即SalesPersonnel.SalesPersonnel，对应的BE_ID为389bfaf0-717d-45f1-83a6-4414b449d275;
            通过"订单编号"这个字段，以及"销售订单"这个表名称，可以确定查询的表涉及销售订单表，即SaleOrder.SaleOrder，对应的BE_ID为0029c056-484c-450f-8ce0-e85528ea7f51;
        回答：389bfaf0-717d-45f1-83a6-4414b449d275;0029c056-484c-450f-8ce0-e85528ea7f51;

        问题：查询每一个客户的总合计实付，按合计实付升序排序
        推理过程：
            通过"客户"这个字段，可以确定查询的表涉及客户表，即Customer.Customer，对应的BE_ID为e6cbbb12-3964-4bc8-90a2-8d07d3d99852;
            通过"实付"这个字段，可以确定查询的表涉及销售订单表，即SaleOrder.SaleOrder，对应的BE_ID为0029c056-484c-450f-8ce0-e85528ea7f51;
        回答：e6cbbb12-3964-4bc8-90a2-8d07d3d99852;0029c056-484c-450f-8ce0-e85528ea7f51;

        问题：查询所有客户的编号、名称
        推理过程：
            通过"客户的编号"、"客户的名称"这些字段,可以确定查询的表涉及客户表,即Customer.Customer，对应的BE_ID为e6cbbb12-3964-4bc8-90a2-8d07d3d99852;
        回答：e6cbbb12-3964-4bc8-90a2-8d07d3d99852;

        问题：查询所有销售订单中有哪些不同的客户
        推理过程：
            通过"销售订单"这个表名称，可以确定查询的表涉及销售订单表，即SaleOrder.SaleOrder，对应的BE_ID为0029c056-484c-450f-8ce0-e85528ea7f51;
            通过"客户"这个字段，发现其存在于销售订单中，此时不用再加入客户表的BE_ID，因为通过销售订单表已经可以查询到客户信息；
        回答：0029c056-484c-450f-8ce0-e85528ea7f51;

        问题：查询共有多少个描述中不包含‘服务好’的销售组织
        推理过程：
            通过"销售组织"这个表名称，可以确定查询的表涉及销售组织表，即SalesOrganization.SalesOrganization，对应的BE_ID为6079cfe2-327b-4f3f-af1e-54b53e293c52;
        回答：6079cfe2-327b-4f3f-af1e-54b53e293c52;

        问题：查询在销售订单中出现的客户的编号、名称、描述
        推理过程：
            通过"客户的编号"、"客户的名称"、"客户的描述"这些字段,可以确定查询的表涉及客户表,即Customer.Customer，对应的BE_ID为e6cbbb12-3964-4bc8-90a2-8d07d3d99852;
            通过"销售订单"这个表名称，可以确定查询的表涉及销售订单表，即SaleOrder.SaleOrder，对应的BE_ID为0029c056-484c-450f-8ce0-e85528ea7f51;
        回答：e6cbbb12-3964-4bc8-90a2-8d07d3d99852;0029c056-484c-450f-8ce0-e85528ea7f51;

        问题：查询没有任何销售人员的销售组织
        推理过程：
            通过"销售组织"这个表名称，可以确定查询的表涉及销售组织表，即SalesOrganization.SalesOrganization，对应的BE_ID为6079cfe2-327b-4f3f-af1e-54b53e293c52;
            通过"销售人员"这个字段，可以确定查询的表涉及销售人员表，即SalesPersonnel.SalesPersonnel，对应的BE_ID为389bfaf0-717d-45f1-83a6-4414b449d275;
        回答：6079cfe2-327b-4f3f-af1e-54b53e293c52;389bfaf0-717d-45f1-83a6-4414b449d275;

请你遵循如下规则：
    1. 当查询内容涉及到的各个字段均在同一个表中时，只需返回该表的BE_ID；
        例如：查询所有销售订单中有哪些不同的客户
            错误返回：0029c056-484c-450f-8ce0-e85528ea7f51;e6cbbb12-3964-4bc8-90a2-8d07d3d99852;
                原因：查询内容涉及到的"客户"已经在销售订单表中，只需返回销售订单表的BE_ID即可，无需再返回客户表的BE_ID；
            正确返回：0029c056-484c-450f-8ce0-e85528ea7f51;

现在，请你根据如下表信息：
    {}
回答问题：{}
'''

BQL_generate_template = '''
你的任务是将输入的数据库信息结合输入的自然语言查询,转换为对应的BQL查询语言。

BQL的介绍:
    BQL是iGIX中提供的基于业务实体的查询语言，基本语法规则如下，你需要尤其理解和遵循这些规则：
        1. BQL以TSql为语法基础，书写时使用的关键字和语法，与TSql一致。
        2. BQL中查询的不是数据库的表名与列名，BQL中的查询对象是业务实体上的节点与属性，可象征性的理解为：业务实体上的节点对应数据库的表，节点上的属性对应数据库表的列。
            简单举例如下：
                销售订单实体(SaleOrder)上想查询ID为0001的订单信息，包括：订单编号、销售人员的名称，BQL书写如下：
                    SELECT SaleOrder.OrderCode, SaleOrder.SalesPersonnel_Name FROM SaleOrder.SaleOrder WHERE SaleOrder.ID = '0001'
                可以看见,其中FROM子句中的SaleOrder.SaleOrder，表示要查询的节点，书写规则为 "实体编号.节点编号" ，SELECT子句与WHERE子句查询的字段，如SaleOrder.Code，表示要查询的字段，书写规则为"节点编号.属性的标签"。其中字段可以是本实体字段，也可以是关联带出字段或UDT带出字段，比如SaleOrder.Employee_Name。
        3. 允许在BQL中使用别名，包括表别名与列别名。
            简单举例如下：
                    SELECT SO.OrderCode AS OC, SO.SalesPersonnel_Name AS SalesPersonnelName FROM SaleOrder.SaleOrder SO WHERE SO.ID = '0001'
                使用别名时与TSql语法一致，其中FROM子句中的SaleOrder.SaleOrder SO，表示将查询的节点重新命名为SO；SO.OrderCode AS OC表示将SO节点(代表SaleOrder节点)上的OrderCode字段重新命名为OC
        4. BQL中,要注意节点和子节点的关系。
            简单举例如下：
                子节点关系,如业务实体A的table_id中"."后面的字段是另一个业务实体B的table_id中的"."前面的字段,则说明业务实体A是业务实体B的父实体。此时若要查询业务实体A的子节点B的信息,则可以在业务实体A上直接查询属于子节点B的字段:
                    例如想要查询销售订单实体(SaleOrder.SaleOrder)上订单详情(SaleOrder.OrderDetail)子节点的信息，包括：商品、金额：
                        SELECT  OrderDetail.Goods,  OrderDetail.Amount FROM  SaleOrder.OrderDetail

    BQL支持的语法:

        SELECT:
            含义: SELECT子句，指定查询返回的列。
            说明: 
            1. 不支持 * 查询，请在子句中明确指定要查询的内容（也不支持count(*)）。
            2. 查询的列可以是业务实体上节点的属性（书写规则请参考上一小节），还可以是各种标量表达式，比如常量、函数以及由一个或多个运算符连接的列名或其任意组合，甚至是子查询。
            3. 如果查询的列不是简单的节点属性，请给该列命名别名columnname AS alias，原因是查询返回的结果需要有列名。
            4. 可以使用DISTINCT关键字，指定在结果集中只能包含唯一行。
            5. 不支持使用TOP关键字。

        FROM:
            含义: FROM子句，可在SELECT语句、DELETE语句以及UPDATE语句中使用。
            说明: 
            1. FROM子句中用到的表可以是实体节点，还可以是派生表（即嵌套其他查询的查询结果）。
            2. 可以为表取别名，取别名后使用表中字段时需要带着表别名的前缀。派生表必须取别名，方便使用。
            3. 支持INNER JOIN, LEFT OUTER JOIN，RIGHT OUTER JOIN，FULL OUTER JOIN关联类型。逗号形式的关联方式语法支持但是不推荐，性能不好而且语句不易扩展。

        WHERE:
            含义: WHERE子句，指定查询返回的行的搜索条件。
            说明: 搜索条件可以是各种布尔表达式的组合，比如以And或Or连接的布尔二元表达式，比较两个标量表达式的布尔表达式，以及LIKE、EXIST、IN等谓词。

        DELETE:
            含义: 从FROM子句中删除一行或多行。
            说明: DELETE语句一般结构为 DELETE FROM XX WHERE search_condition。

        UPDATE:
            含义: 更新现有数据的语句。
            说明: 
            update语句主要有两种：
            1.普通的单表更新的UPDATE语句： UPDATE SalesOrder.SalesOrder SET SalesOrder.AuditState = 'Submit' WHERE *search_condition*。
            2.UPDATE-SET-FROM结构的更新语句，基于其他表中的数据更新数据：UPDATE Customer.Customer SET Customer.Description = CONCAT(Customer.Description, Credit.Code) FROM Credit.Credit WHERE Customer.Credit = Credit.ID。

        INSERT:
            含义: 插入语句。
            说明: INSERT语句必须要提供插入列的列表。 INSERT语句有两种句式：
            1.INSERT-INTO-VALUES 插入指定值到表中，比如：INSERT INTO Credit.Credit(Credit.ID, Credit.Code, Credit.Name) VALUES(NEWID(), 'A', 'A'), (NEWID(), 'AA', 'AA')。
            2.INSERT-INTO-SELECT 将从其他表中查询的数据插入到表中，比如：INSERT INTO Credit.Credit(Credit.ID, Credit.Code, Credit.Name) SELECT newid(), CustomerCredit.Code, CustomerCredit.Name FROM CustomerCredit.CustomerCredit。

        UNION:
            含义: 将两个查询的结果连接到一个结果集中。
            说明: 可控制结果集是否包含重复行，UNION ALL包含重复行，UNION排除重复行。由于UNION要进行重复值扫描，所以效率低。如果合并没有刻意要删除重复行，那么就使用UNION ALL。

        GROUP BY:
            含义: 将查询结果划分为多个行组的子句，通常用于在每个组上执行一个或多个聚合。
            说明: 
            GROUP BY语句用于结合合计函数，根据一个或多个列对结果集进行分组。
            比如在订单列表中查询每个销售人员的总订单额：SELECT SalesOrder.Salesrep_Name, SUM(SalesOrder.TotalPrice) FROM SalesOrder.SalesOrder GROUP BY SalesOrder.Salesrep。

        ORDER BY:
            含义: 对查询返回的数据进行排序。
            说明:
            1.order_by_expression指定用于对查询结果集进行排序的列或表达式。
            2.可以指定多个排序列，用逗号分隔。
            3.默认是升序ASC，降序为DESC。

    BQL支持的表达式：
        表达式分为标量表达式与布尔表达式两种：
        1. 标量表达式: 包括列、函数、常量、变量等简单的表达式，以及这些简单表达式的一元、二元运算，标量表达式运算后的结果仍然是标量表达式。此外CASE-WHEN语句也属于标量表达式，可以使用在SELECT子句中做简单的判断。更复杂的，标量表达式还可以是一个子查询。
        2. 布尔表达式：布尔表达式的运算结果是true或者false。布尔表达式包括比较布尔表达式、二元、三元以及判空的布尔表达式，还包括Exist谓词、In谓词、Like谓词。

        具体如下：
        
            标量表达式:

                简单标量表达式:
                    含义: 包括列、函数、常量、变量等基本元素。
                    说明:
                    列：即BE实体上节点的属性，表达方式为"节点编号.属性标签"。
                    函数：详细内容在第三节中介绍。
                    常量：支持整型Integer、精度Numeric、字符型String。
                    变量：格式为@ para_name。

                一元运算:
                    含义: 对单个表达式应用的运算符。
                    说明: 常用的一元算符包括+、-，例如：-SalesOrder.Rate。

                二元运算:
                    含义: 对两个表达式进行运算的运算符。
                    说明: 常用的二元运算符包括+、-、*、/、%，例如：OrderItem.TotalAmount * OrderItem.TaxInPrice。

                CASE-WHEN:
                    含义: 条件语句，用于在不同条件下返回不同的值。
                    说明:
                    简单型CASE-WHEN: 根据客户的信用等级返回不同的值normal、fine、perfect或unknown:
                        SELECT Customer.Name, CASE Customer.Credit_Code WHEN 'A' THEN 'normal' WHEN 'AA' THEN 'fine' WHEN 'AAA' THEN 'perfect' ELSE 'unknown' END AS Credit FROM Customer.Customer
                    查找型CASE-WHEN: 根据订单项单价的大小范围执行不同的计算政策:
                        SELECT OrderItem.Code, CASE WHEN OrderItem.TaxInprice > 400 THEN OrderItem.SaleQu * TaxInPrice * 0.8 WHEN OrderItem.TaxInprice < 300 THEN OrderItem.SaleQu * TaxInPrice ELSE '固定值' END AS calc FROM SalesOrder.OrderItem

                括号 ():
                    含义: 用于明确表达式中的运算优先级。
                    说明: 标量表达式中支持使用括号来表达运算的优先级。

            布尔表达式:

                比较布尔表达式:
                    含义: 对两个标量表达式进行比较，返回布尔值。
                    说明: 常用比较类型包括：= > < >= <=

                二元布尔表达式:
                    含义: 对两个布尔表达式进行二元运算。
                    说明: 常用运算类型包括：AND、OR。

                三元布尔表达式:
                    含义: 使用(NOT) BETWEEN AND进行三元运算。
                    说明: 例如，订单总额在0到10000之间返回true：SalesOrder.TotalAmount BETWEEN 0 AND 100000
                
                判空:
                    含义: 判断标量表达式是否为空。
                    说明: 使用IS (NOT) NULL，例如判断订单销售人员是否为空：SalesOrder.Salesrep IS NULL

                括号 ():
                    含义: 用于在布尔表达式中明确运算的优先级。

                EXISTS谓词:
                    含义: 指定一个子查询，测试行是否存在。
                    说明: 例如，查找所有已开单的销售人员：
                    SELECT Salesrep.Name FROM Salesrep.Salesrep WHERE EXISTS (SELECT SalesOrder.Salesrep FROM SalesOrder.SalesOrder WHERE SalesOrder.Salesrep = Salesrep.ID)

                IN谓词:
                    含义: 确定指定的值是否与子查询或列表中的值相匹配。
                    说明:
                    test_expression [NOT] IN (expression [, … n ])：IN后面是一个表达式列表，例如查找所有信用等级为A及以上的客户名单：
                        SELECT Customer.Name FROM Customer.Customer WHERE Customer.Credit_Code IN ('A', 'AA', 'AAA')
                    test_expression [NOT] IN (subquery)：IN后面是一个子查询，例如查找所有山东区销售人员的订单信息：
                        SELECT SalesOrder.ID, SalesOrder.CODE FROM SalesOrder.SalesOrder WHERE SalesOrder.Salesrep IN (SELECT Salesrep.ID FROM Salesrep.Salesrep WHERE Salesrep.OrgID = 'xx')

                LIKE谓词:
                    含义: 确定特定字符串是否与指定模式相匹配，模式可以包含常规字符和通配符。
                    说明: 例如，查找所有编号（不）包含B的信用等级：SELECT Credit.Name FROM Credit.Credit WHERE Credit.Code (NOT) LIKE '%B%'

    BQL目前支持的函数如下:
        聚合函数:
            含义: 用于对一组数据执行聚合操作。
            说明: 常用的聚合函数包括AVG、COUNT、MAX、MIN、SUM。

        数学函数:
            含义: 用于执行各种数学计算。
            说明: 常用的数学函数包括ABS、CEILING、FLOOR、ROUND。
        
        字符串函数:
            含义: 用于操作和处理字符串。
            说明: 常用的字符串函数包括CONCAT、SUBSTRING、LEN、REPLACE、LEFT、RIGHT、LTRIM、RTRIM、TRIM、REVERSE、FIRSTPART、LASTPART、UPPER、LOWER。
        
        日期函数:
            含义: 用于操作和处理日期数据。
            说明: 常用的日期函数包括DAY、MONTH、YEAR、DATEPART、GETDATE、DATEADD、DAYDIFF。

        转换函数:
            含义: 用于将数据从一种数据类型转换为另一种数据类型。
            说明: 常用的转换函数包括CAST、TO_CHAR。

        其他函数:
            含义: 其他常用的辅助函数。
            说明: 常用的其他函数包括ISNULL、NEWID、ROW_NUMBER、COALESCE。

        函数详细说明如下：

            聚合函数如下：
                AVG:
                    含义: 聚合函数，返回组中各值的平均值。
                    格式: AVG(expression)，其中expression为列或者标量表达式。
                    举例: AVG(Bonus) 返回奖金列Bonus的平均值。

                COUNT:
                    含义: 聚合函数，返回组中找到的项数量，返回int数据类型值。
                    格式: COUNT(expression)，其中expression为列或者标量表达式。
                    举例: COUNT(EmployeeID) 返回雇员数量。

                MAX:
                    含义: 聚合函数，返回表达式中的最大值。
                    格式: MAX(expression)，其中expression为列或者标量表达式。
                    举例: MAX(TaxRate) 返回税率列TaxRate中的最高税率。

                MIN:
                    含义: 聚合函数，返回表达式中的最小值。
                    格式: MIN(expression)，其中expression为列或者标量表达式。
                    举例: MIN(TaxRate) 返回税率列TaxRate中的最低税率。

                SUM:
                    含义: 聚合函数，返回表达式中所有值的和。
                    格式: SUM(expression)，其中expression为列或者标量表达式。
                    举例: SUM(Price) 返回价格列Price相加的总和。

            注: 聚合函数支持DISTINCT关键字，比如COUNT(DISTINCT EmployeeID)返回去重后的雇员数量。

            数学函数如下:

                ABS:
                    含义: 数学函数，返回指定数值表达式的绝对值（正值）。
                    格式: ABS(numeric_expression)，其中numeric_expression为数值类型的列或表达式。
                    举例: ABS(-1.0) 返回1.0。
                
                CEILING:
                    含义: 数学函数，返回大于或等于指定数值表达式的最小整数，即向上取整。
                    格式: CEILING(numeric_expression)，其中numeric_expression为精确数值或近似数值数据类型类别的表达式。返回值与numeric_expression相同类型。
                    举例: CEILING(123.45) 返回124.00，CEILING(-123.45) 返回-123.00，CEILING(0.0) 返回0.00。

                FLOOR:
                    含义: 数学函数，返回小于或等于指定数据表达式的最大整数，即向下取整。
                    格式: FLOOR(numeric_expression)，其中numeric_expression是精确数值或近似数值数据类型类别的表达式。返回值类型与numeric_expression相同。
                    举例: FLOOR(123.45) 返回123，FLOOR(-123.45) 返回-124。

                ROUND:
                    含义: 数学函数，返回一个数值，舍入到指定的长度或者精度。
                    格式: ROUND(numeric_expression, length)，其中numeric_expression为数值类型的列或表达式，length是舍入精度。若length为正数，则将表达式舍入到length指定的小数位数；若length为负数，则在小数点左边舍入。
                    举例: ROUND(123.9994, 3) 返回123.9990，ROUND(748.58, -2) 返回700.00。

            字符串函数如下:

                CONCAT:
                    含义: 字符串函数，返回通过串联或联接两个或更多字符串值生成的字符串。
                    格式: CONCAT(string_value1, string_value2 [, string_valueN ])，其中string_value为要与其他值串联的字符串值，至少需要两个。
                    举例: CONCAT('Happy ', 'Birthday ', 11, '/', '25') 返回Happy Birthday 11/25；CONCAT(FirstName, LastName) 返回FirstName列与LastName列连接的字符串。
                
                SUBSTRING:
                    含义: 字符串截取函数，用于从字符串中提取指定长度的子串。
                    格式: SUBSTRING(expression, start, length)，其中expression为字符串列或表达式，start指定返回字符的起始位置（从1开始），length为返回字符数。
                    举例: SUBSTRING('abcdef', 2, 3) 返回bcd。
                
                LEN:
                    含义: 字符串函数，返回指定字符串表达式的字符数，返回int数据类型值。
                    格式: LEN(string_expression)，其中string_expression为要计算的字符列或字符串表达式。
                    举例: LEN(FirstName) 返回FirstName列的字符数。
            
                REPLACE:
                    含义: 字符串函数，用于将字符串中的所有指定字符替换为另一个字符。
                    格式: REPLACE(string_expression, string_pattern, string_replacement)，其中string_expression是要搜索的字符串，string_pattern是要查找的子字符串，string_replacement是替换字符串。
                    举例: REPLACE('abcdefghicde', 'cde', 'xxx') 返回abxxxfghixxx。
                LEFT:
                    含义: 字符串函数，返回字符串中从左边开始指定个数的字符。
                    格式: LEFT(character_expression, integer_expression)，其中character_expression为字符串类型的表达式，integer_expression为指定要返回的字符数的正整数。
                    举例: LEFT('abcdefg', 2) 返回字符串abcdefg中最左边的两个字符ab。
                
                RIGHT:
                    含义: 字符串函数，返回字符串中从右边开始指定个数的字符。
                    格式: RIGHT(character_expression, integer_expression)，其中character_expression为字符串类型的表达式，integer_expression为指定要返回的字符数的正整数。
                    举例: RIGHT(FirstName, 5) 返回FirstName列中的每个人名字最右边的5个字符。
                
                LTRIM:
                    含义: 字符串函数，返回删除了前导空格之后的字符表达式。
                    格式: LTRIM(character_expression)，其中character_expression为字符串类型的表达式。
                    举例: LTRIM(' five') 返回five。
                
                RTRIM:
                    含义: 字符串函数，截断所有尾随空格后返回一个字符串。
                    格式: RTRIM(character_expression)，其中character_expression为字符串类型的表达式。
                    举例: RTRIM('spaces ') 返回spaces。

                TRIM:
                    含义: 字符串函数，删除字符串开头和结尾的空格字符。
                    格式: TRIM(character_expression)，其中character_expression为字符串类型的表达式。
                    举例: TRIM(' test ') 返回test。

                REVERSE:
                    含义: 字符串函数，返回字符串值的逆序。
                    格式: REVERSE(string_expression)，其中string_expression为字符串类型的表达式。
                    注意: string_expression中请不要包含汉字，在Oracle数据库中使用REVERSE函数时若包含汉字，可能会出现乱码。
                    举例: REVERSE('abcd') 返回dcba。
                
                FIRSTPART:
                    含义: 字符串函数，截取分隔符在字符串中首次出现之前的片段。
                    格式: FIRSTPART(string_expression, string_delim)，其中string_expression为要截取的字符串，string_delim为分隔符；如果string_expression中没有找到指定的分隔符，将返回string_expression本身。
                    举例: FIRSTPART('自行车-三轮车-摩托车-小汽车', '-') 返回自行车；FIRSTPART('AAA', 'B') 返回AAA。
                
                LASTPART:
                    含义: 字符串函数，截取分隔符在字符串中最后一次出现之后的末段片段。
                    格式: LASTPART(string_expression, string_delim)，其中string_expression为要截取的字符串，string_delim为分隔符；如果string_expression中没有找到指定的分隔符，将返回string_expression本身。
                    举例: LASTPART('自行车-三轮车-摩托车-小汽车', '-') 返回小汽车；LASTPART('AAA', 'B') 返回AAA。
                
                UPPER:
                    含义: 字符串函数，将小写字符转换为大写字符后返回字符表达式。
                    格式: UPPER(character_expression)，其中character_expression为字符串类型的表达式。
                    举例: UPPER('abcd') 返回ABCD。
                    
                LOWER:
                    含义: 字符串函数，将大写字符转换为小写字符后返回字符表达式。
                    格式: LOWER(character_expression)，其中character_expression为字符串类型的表达式。
                    举例: LOWER('ABCD') 返回abcd。

            日期函数如下:
                DAY:
                    含义: 日期函数，返回表示指定日期date的日期（某月的一天）的整数。
                    格式: DAY(date)，其中date为日期类型的列或表达式。
                    举例: DAY(SalesOrder.PlaceDate) 返回订单日期列中的日。

                MONTH:
                    含义: 日期函数，返回表示指定日期的月份的整数。
                    格式: MONTH(date)，其中date为日期类型的列或表达式。
                    举例: MONTH(SalesOrder.PlaceDate) 返回订单日期列中的月份。

                YEAR:
                    含义: 日期函数，返回表示指定日期的年份的整数。
                    格式: YEAR(date)，其中date为日期类型的列或表达式。
                    举例: YEAR(SalesOrder.PlaceDate) 返回订单日期列中的年份。

                DATEPART:
                    含义: 日期截取函数，返回指定日期的指定部分。
                    格式: DATEPART(datepart, date)，其中date为日期类型的列或表达式，datepart参数表示要截取的部分，支持以下枚举项：year表示截取年份，month表示截取月份，day表示截取日期，hour表示截取小时，minute表示截取分钟，second表示截取秒。
                    举例: 假设订单日期为'2007-10-30 12:15:32.1234567'，DATEPART(year, SalesOrder.PlaceDate)、DATEPART(month, SalesOrder.PlaceDate)、DATEPART(day, SalesOrder.PlaceDate)分别返回2007、10、30。
                
                GETDATE:
                    含义: 日期函数，返回当前数据库系统时间戳，返回值类型为datetime。
                    格式: GETDATE()。
                    举例: 无需参数，直接调用返回当前日期和时间。

                DATEADD:
                    含义: 日期函数，将指定的number值（作为带符号整数）与输入date值的指定datepart相加，然后返回该修改后的值。
                    格式: DATEADD(datepart, number, date)，其中：
                    datepart表示要与整数值相加的日期部分，支持year、quarter、month、day、week（不需要加单引号）。
                    number为整型表达式。
                    date为日期类型的表达式或变量。
                    举例: DATEADD(day, -5, GETDATE()) 返回当前日期减5天后的日期值；DATEADD(month, 3, SalesOrder.PlaceDate) 返回订单日期加3个月后的日期值。
                
                DAYDIFF:
                    含义: 日期函数，返回指定的startdate和enddate两个日期之间所跨的天数（带符号的整数值）。
                    格式: DAYDIFF(startdate, enddate)，其中startdate和enddate为日期类型的列、表达式或变量。
                    举例: DAYDIFF(SalesOrder.PlaceDate, GETDATE()) 返回订单日期与当前日期相差的天数（即当前日期减去订单日期）。

            转换函数如下:
                CAST:
                    含义: 转换函数，将表达式由一种数据类型转换为另一种数据类型。
                    格式: CAST(expression AS data_type[(length)])，其中expression为列或表达式，data_type为目标数据类型，length为指定目标数据类型长度的可选整数（适用于可指定长度的数据类型）。
                    举例: CAST(SalesOrder.PlaceDate AS char(100)) 将订单日期转换为文本。

                TO_CHAR:
                    含义: 转换函数，将日期类型的列或表达式转换为指定格式的文本。
                    格式: TO_CHAR(date_expression, format_string)，其中date_expression为日期类型的列或表达式，format_string为格式化字符串。常用格式：yyyy表示四位年份，MM表示两位月份，dd表示两位日期。
                    举例: TO_CHAR(SalesOrder.PlaceDate, 'yyyy.MM.dd') 将返回以'2020.05.30'格式的字符串；TO_CHAR(SalesOrder.PlaceDate, 'yyyy-MM-dd') 将返回以'2020-05-30'格式的字符串。


            其他函数如下:
                ISNULL:
                    含义: 用指定的替换值替换NULL。
                    格式: ISNULL(check_expression, replacement_value)，其中check_expression为将被检查是否为NULL的列或表达式，replacement_value为NULL时返回的值。如果check_expression不为NULL，则返回该表达式的值，否则返回replacement_value。
                    举例: ISNULL(Salesrep.Description, 'Default') 若销售人员的描述为NULL，则返回字符串'Default'。
                
                NEWID:
                    含义: 创建uniqueidentifier类型的唯一值（通常用于生成GUID）。
                    格式: NEWID()。
                    举例: 常用于需要创建GUID的场景中。
                
                ROW_NUMBER:
                    含义: 对结果集的输出进行编号，返回结果集分区内行的序列号，每个分区的第一行从1开始。通常与聚合及开窗函数配合使用。
                    格式: ROW_NUMBER() OVER([PARTITION BY value_expression [, … n]] ORDER BY order_by_clause)。
                    举例: ROW_NUMBER() OVER(PARTITION BY Salesrep.OrgID ORDER BY Salesrep.Code ASC) 销售人员按所属区域分区并按编号升序排列的结果进行编号。
                
                COALESCE:
                    含义: 按顺序计算变量并返回最初不等于NULL的第一个表达式的当前值。
                    格式: COALESCE(expression [, … n])，其中expression为任何类型的表达式。
                    举例: COALESCE(colA, colB, colC) 顺序检查colA、colB、colC三列中第一个不为NULL的列。
                
                GETEXTENDFIELDS:
                    含义: 获取指定实体节点的所有扩展字段的集合。
                    格式: GETEXTENDFIELDS(paramString)，其中paramString有两种格式：一种是"BeCode.NodeCode"的两段式；另一种是"TableAlias"表别名方式。
                    举例: 该函数返回指定实体节点的所有扩展字段的集合（不区分维度且包括扩展字段的关联带出字段）。该函数仅在查询语句中使用，请勿在其他类型的语句中使用。

你可以参考的若干个例子：
    举例一
        这是相关的表结构:
            BE_ID: 0029c056-484c-450f-8ce0-e85528ea7f51
                table_id: SaleOrder.SaleOrder
                table_name: 销售订单
                字段信息:
                    SaleOrder.ID: 主键
                    SaleOrder.Version: 版本
                    SaleOrder.BillStatus: 状态
                    SaleOrder.OrderCode: 订单编号
                    SaleOrder.SalesPersonnel: 销售人员
                    SaleOrder.SalesPersonnel_Code: 编号
                    SaleOrder.SalesPersonnel_Name: 名称
                    SaleOrder.PayMethod: 支付方式
                    SaleOrder.Customer: 客户
                    SaleOrder.Customer_Code: 编号
                    SaleOrder.Customer_Name: 名称
                    SaleOrder.Telephone: 联系电话
                    SaleOrder.SendState: 发货状态
                    SaleOrder.Remark: 备注
                    SaleOrder.TotalPrice: 订单金额
                    SaleOrder.TotalDiscounts: 折扣优惠
                    SaleOrder.ActualPay: 合计实付
                    SaleOrder.OrderSource: 订单来源
                    SaleOrder.DateTime: 下单日期
                    SaleOrder.Ordertime: 下单时间

            BE_ID: 0029c056-484c-450f-8ce0-e85528ea7f51
                table_id: SaleOrder.OrderDetail
                table_name: 订单明细
                字段信息:
                    OrderDetail.ID: 主键
                    OrderDetail.ParentID: 上级对象主键
                    OrderDetail.Goods: 商品
                    OrderDetail.Goods_GoodsName: 商品名称
                    OrderDetail.Goods_GoodsCode: 商品编号
                    OrderDetail.Goods_Category: 分类名称
                    OrderDetail.Specification: 规格型号
                    OrderDetail.Quality: 数量
                    OrderDetail.Price: 标准单价
                    OrderDetail.Amount: 金额
                    OrderDetail.DiscountType: 折扣类型
                    OrderDetail.Discount: 折扣金额
                    OrderDetail.ActualAmount: 实际结算金额
                    OrderDetail.Remark: 备注

        现在请你根据上述的BQL规则以及参考例子，结合相关的表结构信息，回答这个问题:
            1.查询所有销售订单的订单编号、订单金额、支付方式：	
                select SaleOrder.OrderCode, SaleOrder.TotalPrice, SaleOrder.PayMethod from SaleOrder.SaleOrder
            2.查询下单年份为2024的所有销售订单的订单编号：	
                select SaleOrder.OrderCode from SaleOrder.SaleOrder where year(SaleOrder.OrderTime) = '2024'
            3.查询下单月份为10月的所有销售订单的订单编号	
                select SaleOrder.OrderCode from SaleOrder.SaleOrder where Month(SaleOrder.OrderTime) = '10'
            4.查询所有月初的销售订单的订单编号	
                select SaleOrder.OrderCode from SaleOrder.SaleOrder where Day(SaleOrder.OrderTime) = '01'
            5.查询下单日期为2024年3月1以后的所有订单金额超过10000的销售订单的订单编号	
                select SaleOrder.OrderCode from SaleOrder.SaleOrder where SaleOrder.TotalPrice > 10000 and TO_CHAR(SaleOrder.DateTime, 'yyyy-MM-dd') > '2024-03-01' 
            6.查询所有订单的订单金额(向下取整)	
                select floor(SaleOrder.TotalPrice) as TotalPrice from SaleOrder.SaleOrder
            7.查询下单时间在2024年的所有订单的平均订单金额	
                SELECT AVG(SaleOrder.TotalPrice) as TotalPrice FROM SaleOrder.SaleOrder WHERE  Year(SaleOrder.OrderTime) = '2024'
            8.查询2024年共有多少条销售订单	
                SELECT Count(1) as count FROM SaleOrder.SaleOrder WHERE Year(SaleOrder.OrderTime) = '2024'
            9.查询2024年订单金额最大的销售订单	
                SELECT MAX(SaleOrder.TotalPrice) as TotalPrice FROM SaleOrder.SaleOrder WHERE Year(SaleOrder.OrderTime) = '2024'
            11.查询2024年订单金额最小的销售订单	
                SELECT MIN(SaleOrder.TotalPrice) as TotalPrice FROM SaleOrder.SaleOrder WHERE DATEPART(Year, SaleOrder.OrderTime) = '2024'
            12.查询所有订单的订单金额总和	
                SELECT Sum(SaleOrder.TotalPrice) as TotalPrice FROM SaleOrder.SaleOrder 
            13.查询备注中包含‘特殊’的销售订单的订单编号	
                select SaleOrder.OrderCode from SaleOrder.SaleOrder WHERE SaleOrder.Remark like '%特殊%'
            14.查询备注中不包含‘特殊’的销售订单的订单编号	
                select SaleOrder.OrderCode from SaleOrder.SaleOrder WHERE SaleOrder.Remark not like '%特殊%'
            15.按订单金额降序查询所有销售订单的订单编号和订单金额	
                select SaleOrder.OrderCode, SaleOrder.TotalPrice from SaleOrder.SaleOrder Order By SaleOrder.TotalPrice DESC
            16.按订单金额升序查询所有销售订单的订单编号和订单金额	
                select SaleOrder.OrderCode, SaleOrder.TotalPrice from SaleOrder.SaleOrder Order By SaleOrder.TotalPrice ASC
            17.查询昨天所有销售订单的订单编号	
                SELECT SaleOrder.OrderCode from SaleOrder.SaleOrder where DAYDIFF(SaleOrder.OrderTime, GETDATE()) = '1'
    举例二
        这是相关的表结构:
            BE_ID: 0029c056-484c-450f-8ce0-e85528ea7f51
                table_id: SaleOrder.SaleOrder
                table_name: 销售订单
                字段信息:
                    SaleOrder.ID: 主键
                    SaleOrder.Version: 版本
                    SaleOrder.BillStatus: 状态
                    SaleOrder.OrderCode: 订单编号
                    SaleOrder.SalesPersonnel: 销售人员
                    SaleOrder.SalesPersonnel_Code: 编号
                    SaleOrder.SalesPersonnel_Name: 名称
                    SaleOrder.PayMethod: 支付方式
                    SaleOrder.Customer: 客户
                    SaleOrder.Customer_Code: 编号
                    SaleOrder.Customer_Name: 名称
                    SaleOrder.Telephone: 联系电话
                    SaleOrder.SendState: 发货状态
                    SaleOrder.Remark: 备注
                    SaleOrder.TotalPrice: 订单金额
                    SaleOrder.TotalDiscounts: 折扣优惠
                    SaleOrder.ActualPay: 合计实付
                    SaleOrder.OrderSource: 订单来源
                    SaleOrder.DateTime: 下单日期
                    SaleOrder.Ordertime: 下单时间

            BE_ID: 0029c056-484c-450f-8ce0-e85528ea7f51
                table_id: SaleOrder.OrderDetail
                table_name: 订单明细
                字段信息:
                    OrderDetail.ID: 主键
                    OrderDetail.ParentID: 上级对象主键
                    OrderDetail.Goods: 商品
                    OrderDetail.Goods_GoodsName: 商品名称
                    OrderDetail.Goods_GoodsCode: 商品编号
                    OrderDetail.Goods_Category: 分类名称
                    OrderDetail.Specification: 规格型号
                    OrderDetail.Quality: 数量
                    OrderDetail.Price: 标准单价
                    OrderDetail.Amount: 金额
                    OrderDetail.DiscountType: 折扣类型
                    OrderDetail.Discount: 折扣金额
                    OrderDetail.ActualAmount: 实际结算金额
                    OrderDetail.Remark: 备注

            BE_ID: e6cbbb12-3964-4bc8-90a2-8d07d3d99852
                table_id: Customer.Customer
                table_name: 客户
                字段信息:
                    Customer.ID: 主键
                    Customer.Version: 版本
                    Customer.Code: 编号
                    Customer.Name: 名称
                    Customer.Telephone: 联系电话
                    Customer.Credit: 信用等级ID
                    Customer.Credit_Code: 编号
                    Customer.Credit_Name: 名称
                    Customer.Description: 描述

        现在请你根据上述的BQL规则以及参考例子，结合相关的表结构信息，回答这个问题:
            1.查询每一个客户的总订单金额，降序排序	
                select Sum(SaleOrder.TotalPrice) as TotalPrice, SaleOrder.Customer from SaleOrder.SaleOrder Group By SaleOrder.Customer Order By TotalPrice DESC
            2.按降序展示每个客户的下单次数	
                select SaleOrder.Customer_name, count(SaleOrder.ID) as ID from SaleOrder.SaleOrder group by SaleOrder.Customer_name order by ID
            3.查询在销售订单中出现的客户的编号、名称、描述	
                SELECT customer.code, customer_name，customer_description FROM customer.customer where customer.id IN (SELECT SaleOrder.customer FROM SaleOrder.SaleOrder);
            4.查询所有信用等级ID为”18SKZO“的客户所下的销售订单的订单编号
                SELECT SaleOrder.OrderCode FROM SaleOrder.SaleOrder LEFT JOIN  Customer.Customer ON SaleOrder.Customer = Customer.ID WHERE Customer.Credit = '18SKZO'
            5.查看2024年3月份商品为笔记本电脑的销售订单的订单编号和客户名称
                SELECT SaleOrder.OrderCode, SaleOrder.Customer_name  FROM SaleOrder.SaleOrder left join SaleOrder.OrderDetail on SaleOrder.ID = OrderDetail.ParentID WHERE to_char(SaleOrder.OrderTime, 'YYYY-MM-DD HH24:MI:SS') >= '2024-03-01 00:00:00.000' AND to_char(SaleOrder.OrderTime, 'YYYY-MM-DD HH24:MI:SS') <=  '2024-03-31 00:00:00.000' AND OrderDetail.Goods_GoodsName = '笔记本电脑'      
            6.查询所有客户的描述不为空的销售订单的订单编号
                SELECT SaleOrder.OrderCode FROM SaleOrder.SaleOrder LEFT JOIN Customer.Customer ON SaleOrder.Customer = Customer.ID WHERE Customer.Description IS NOT NULL
            7.查询客户为客户一、客户二、客户三的所有销售订单的订单编号
                SELECT SaleOrder.OrderCode FROM SaleOrder.SaleOrder WHERE SaleOrder.Customer_Name IN ('客户一', '客户二', '客户三')
            8.查询客户除了客户一以外的所有销售订单的发货状态
                SELECT SaleOrder.SendState FROM SaleOrder.SaleOrder WHERE SaleOrder.Customer_Name NOT IN ('客户一')
            9.查询没有任何销售订单的客户的信用等级ID
                SELECT Customer.Credit FROM Customer.Customer WHERE NOT EXISTS (SELECT 1 FROM SaleOrder.SaleOrder WHERE SaleOrder.Customer = Customer.ID)
            10.查询所有下单客户以及客户表中的姓名
                SELECT SaleOrder.Customer_Name FROM SaleOrder.SaleOrder UNION SELECT Customer.Name FROM Customer.Customer

请遵循如下的原则进行回答：
1.标准的输出是一个正确的BQL语句，其中BQL语句请以一行的格式写出，请去掉任何多余的标记，例如返回"SELECT DISTINCT SaleOrder.Customer_Name FROM SaleOrder.SaleOrder"而不要返回"```sql\nSELECT DISTINCT SaleOrder.Customer_Name FROM SaleOrder.SaleOrder\n```"，你只需要只返回一行干净的BQL查询语句。
2.请你在回答问题前,仔细检查问题的中涉及到的字段是否存在同一张表中,若存在,请不要使用JOIN操作,在一张表中查询即可。
3.请你打算进行JOIN操作前，检查涉及到的表格是否是父子表关系,如表A的table_id中"."后面的字段是另一个表B的table_id中的"."前面的字段,则说明表A是表B的父表,此时如果父表包含了所有的需要查询的数据，请直接使用父表进行查询,不要使用JOIN操作
    如：
        想要查询销售订单实体(SaleOrder)上订单详情(OrderDetail)子节点的信息，包括：商品、金额：
            错误示例：SELECT OrderDetail.Goods, OrderDetail.Amount FROM SaleOrder.SaleOrder LEFT JOIN SaleOrder.OrderDetail ON SaleOrder.ID = OrderDetail.ParentID
            正确示例：SELECT  OrderDetail.Goods,  OrderDetail.Amount FROM  SaleOrder.OrderDetail
4.当涉及到具体的年份和月份时间时:
    1.如果是跨月份的时间，清你使用TO_CHAR函数将时间转换为字符串进行比较，例如：TO_CHAR(SaleOrder.DateTime, 'yyyy-MM-dd') > '2024-03-01'
    2.如果是仅为某个具体月份内的时间，请你使用YEAR，MONTH函数进行比较，例如：YEAR(SaleOrder.DateTime) = '2024' AND MONTH(SaleOrder.DateTime) = '02'，这里要注意月份的格式，如果是一位数的月份，需要在前面加0，例如：'02'。
    3.请注意,如果查询明确是某个时间之后,例如查询2024年3月1日之后的数据,则使用大于号,而不是大于等于号,例如查询2024年三月1日以后:TO_CHAR(SaleOrder.DateTime, 'yyyy-MM-dd') > '2024-03-01'
    4.请注意，如果是查询某个时间之前的数据，使用小于号，而不是小于等于号，例如查询2024年三月1日之前的数据：TO_CHAR(SaleOrder.DateTime, 'yyyy-MM-dd') < '2024-03-01'
    5.请注意，如果是查询某个时间以来的数据，使用大于等于号，例如查询2024年三月1日以来的数据：TO_CHAR(SaleOrder.DateTime, 'yyyy-MM-dd') >= '2024-03-01'
5.请优先使用唯一字段进行查询,例如当涉及查询每一个客户或者不同客户或者时,请查询SaleOrder.Customer字段而不使用SaleOrder.Customer_Name字段，因为Customer字段是唯一的，而Customer_Name字段可能会重复，除非特别指明要查询客户的名称
6.当涉及最大、最小的值查询时，要注意BQL禁止使用TOP关键字，请不要出现类似"TOP 1"这样的语句，以及也要注意查询中是否限制了返回的数据条数，如果出现了类似"一条"的描述，那么请注意查询中限制返回的数据条数，例如使用LIMIT 1
这是相关的表结构:
    {}
现在请你根据上述的BQL规则以及参考例子，结合相关的表结构信息，回答这个问题:{}
'''