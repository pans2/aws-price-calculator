<?php
//连接数据库并读取数据表
$servername = "database-1.csmg1iyz8zqb.us-east-2.rds.amazonaws.com"; //服务器连接名
$username = "admin"; //数据库用户名
$password = "changeme"; //数据库密码
$dbname = "testdemo_global"; //数据库名
$conn = new mysqli($servername, $username, $password, $dbname); //连接数据库
echo "<table border='2' bordercolor='#66ccff'>";
if (!$conn) {
	die("连接失败：" . mysqli_connect_error()); //连接数据库失败则杀死进程
}
$instance=$_POST['instance'];
$vcpu=$_POST['vcpu'];
$os=$_POST['os'];
$region=$_POST['region'];
$presw=$_POST['sw'];
$tenancy=$_POST['tenancy'];
$sql = "SELECT * FROM demo002 where type like '%$instance%' and vcpu like '$vcpu' and os like '%$os%' and location like '%$region%' and tenancy like '%$tenancy%' and pre_installedSW like '%$presw%'"; //查询语句--查询数据库表
$result = mysqli_query($conn, $sql);

echo "<table border='1'><tr><td>type</td><td>vcpu</td><td>memory</td><td>location</td><td>tenancy</td><td>OS</td><td>预装软件</td><td>按需每小时价格(USD)</td><td>按需每月价格(USD)</td><td>按需每年价格(USD)</td><td>一年RI价格(USD)</td><td>三年RI价格(USD)</td>";
if (mysqli_num_rows($result) > 0) {
	while ($row = mysqli_fetch_assoc($result)) {
			echo "<tr><td>{$row['type']}</td>";
			echo "<td>{$row['vcpu']}</td>";
			echo "<td>{$row['memory']}</td>";
                        echo "<td>{$row['location']}</td>";
                        echo "<td>{$row['tenancy']}</td>";
                        echo "<td>{$row['os']}</td>";
			echo "<td>{$row['pre_installedSW']}</td>";
                        echo "<td>{$row['on_demand_price']}</td>";
                        echo "<td>{$row['OD_month_744hours']}</td>";
                        echo "<td>{$row['OD_year_365days']}</td>";
                        echo "<td>{$row['all_upfront_price_1yr']}</td>";
			echo "<td>{$row['all_upfront_price_3yr']}</td>";
			echo "</tr>";
	}
} else {
	echo "0 结果";
}
echo "</table>";
mysqli_close($conn); //关闭数据库
