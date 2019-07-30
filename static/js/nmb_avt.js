function change_avt(id){
    $("#avt_main").attr("src","\static/pic/loading.gif");
    $.ajax({url:"/avatar",
            type:"UPDATE",
            async:true,
            data:{
                avatar:id,
            },
            success:function(result){
                console.log(parseInt(result)+'change kookie OK!');
                if(parseInt(result)==1){
                avt_get();
                }
                else{  
                    console.log(result);
                }
            },
            error:function(jqXHR,testStatus,errorThrown){
                //var a = document.getElementById("kookie_main");
                //a.innerText = "未通过邮箱验证";
                alert(errorThrown);
            }
            
        })
}
function avt_get(){
    $.ajax({
        url:"/avatar",
        type:"GET", 
        success:function(result){
            //console.log(result);
            $("#avt_main").attr("src","\static/avatars/"+result+".jpg");
            }
        }
    )
}