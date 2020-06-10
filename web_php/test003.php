<?php
//连接数据库并读取数据表
$servername = "database-1.csmg1iyz8zqb.us-east-2.rds.amazonaws.com"; //服务器连接名
$username = "admin"; //数据库用户名
$password = "changeme"; //数据库密码
$dbname = "testdemo"; //数据库名
$conn = new mysqli($servername, $username, $password, $dbname); //连接数据库
echo "<table border='2' bordercolor='#66ccff'>";
if (!$conn) {
	die("连接失败：" . mysqli_connect_error()); //连接数据库失败则杀死进程
}
$rtype=$_POST['rtype'];
$rengine=$_POST['rengine'];
$rregion=$_POST['rregion'];
$rlicense=$_POST['rlicense'];
$sql = "SELECT * FROM rdsdemo2 where type like '%$rtype%' and databaseEngine like '%$rengine%' and location like '%$rregion%' and licenseModel like '%$rlicense%'"; //查询语句--查询数据库表
$result = mysqli_query($conn, $sql);

echo "<table border='1'><tr><td>type</td><td>vcpu</td><td>memory</td><td>location</td><td>数据库引擎</td><td>许可模式</td><td>按需每小时价格</td><td>按需每月价格</td><td>按需每年价格</td><td>一年RI价格</td>";
if (mysqli_num_rows($result) > 0) {
	while ($row = mysqli_fetch_assoc($result)) {
			echo "<tr><td>{$row['type']}</td>";
			echo "<td>{$row['vcpu']}</td>";
			echo "<td>{$row['memory']}</td>";
                        echo "<td>{$row['location']}</td>";
                        echo "<td>{$row['databaseEngine']}</td>";
                        echo "<td>{$row['licenseModel']}</td>";
                        echo "<td>{$row['on_demand_price']}</td>";
                        echo "<td>{$row['OD_month_744hours']}</td>";
                        echo "<td>{$row['OD_year_365days']}</td>";
                        echo "<td>{$row['all_upfront_price_1yr']}</td>";
			echo "</tr>";
	}
} else {
	echo "0 结果";
}
echo "</table>";
mysqli_close($conn); //关闭数据库
