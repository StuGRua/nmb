function GetUrlParam(paraName) {
    　　	var url = document.location.toString();
    　　　　var arrObj = url.split("?");
    　　　　if (arrObj.length > 1) {
    　　　　　　var arrPara = arrObj[1].split("&");
    　　　　　　var arr;
    
    　　　　　　for (var i = 0; i < arrPara.length; i++) {
    　　　　　　　　arr = arrPara[i].split("=");
    
    　　　　　　　　if (arr != null && arr[0] == paraName) {
    　　　　　　　　　　return arr[1];
    　　　　　　　　}
    　　　　　　}
    　　　　　　return "";
    　　　　}
    　　　　else {
    　　　　　　return "";
    　　　　}
    　　	}
function check(v_psw) 
            {
                psw=document.getElementById("res_pass").value;
                if(psw!=v_psw) 
                {
                    alert("两次密码不相同！");
                    document.getElementById("res_submit").disabled="disabled";
                }
                else
                {
                    document.getElementById("res_submit").disabled="";
                }
            }
function enc(id){
                    //alert("123");
                    //var password = $("#password1").val();
                    var password = $(id).val();
                    //alert(password);
                    var passwd = hex_md5(password);//就是我们要的
                    //alert(passwd);
                    document.getElementById("password1").value=passwd;
                }
function enc_all(){
                var password=$("#res_pass1").val();
                var passwd = hex_md5(password);
                document.getElementById("res_pass1").value=passwd;
                var password=$("#res_pass").val();
                var passwd = hex_md5(password);
                document.getElementById("res_pass").value=passwd; 
    
            }		
function encoderOn(){
				$("#encoderFrame").attr("width","300px");
				$("#encoderFrame").attr("height","200px");
				$("#encoderFrame").attr("frameborder","1");
			} 
function encoderOff(){
				$("#encoderFrame").attr("width","0px");
				$("#encoderFrame").attr("height","0px");
				$("#encoderFrame").attr("frameborder","0");
            }
function copyToText(){
                var a = document.getElementById('encoderFrame').contentWindow.document.getElementById('encoded-area').value;
                alert(a);
                document.getElementById("post_content").value=a;
            }
function pic_inserted(){
                document.getElementById("reply1").value+="[图片]";
            }