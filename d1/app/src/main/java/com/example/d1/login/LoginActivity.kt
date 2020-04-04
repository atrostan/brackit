package com.example.d1.login

import android.content.Intent
import android.content.pm.ActivityInfo
import android.os.AsyncTask
import android.os.Bundle
import android.view.MenuItem
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.d1.MainActivity
import com.example.d1.R
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

import java.io.IOException;


class LoginActivity : AppCompatActivity() {
    var client = OkHttpClient()
    val requestURL = "http://10.0.2.2:5000/api/"
    //val requestURL = "http://172.20.10.2:5000/api/"
    var token = ""
    var user = ""


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        setContentView(R.layout.activity_login)
        title = "Login"

        val username = findViewById<EditText>(R.id.username) as EditText
        val password = findViewById<EditText>(R.id.password) as EditText
        val login = findViewById<Button>(R.id.login) as Button
        var signup = findViewById<Button>(R.id.register) as Button
        //val loading = findViewById<ProgressBar>(R.id.loading) as ProgressBar


        login.setOnClickListener {
            val nameStr = username.text.toString()
            val passStr = password.text.toString()

            getlogin(nameStr,passStr)
        }

        signup.setOnClickListener{
            val nameStr = username.text.toString()
            val passStr = password.text.toString()

            if (!nameStr.isEmpty() && !passStr.isEmpty() && nameStr.contains("@")){
                Thread{
                    register(nameStr,passStr)
                }.start()

            }


        }

        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

    }

    private fun register(name:String,pass:String){
        val client = OkHttpClient()

        var jobject = JSONObject()
        var username = name.split("@")[0]
        jobject.put("username",username)
        jobject.put("password",pass)
        jobject.put("email",name)

        val mediaType = "application/json; charset=utf-8".toMediaType()

        //192.168.0.33    172.17.184.246
        val request = Request.Builder()
            .url(requestURL+"users")
            .post(jobject.toString().toRequestBody(mediaType))
            .build()

        client.newCall(request).execute().use { response ->
           // if (!response.isSuccessful) throw IOException("Unexpected code $response")

            if (response.code == 400){
                runOnUiThread{
                    Toast.makeText(this@LoginActivity, "User already exist", Toast.LENGTH_SHORT).show()
                }

            }else if (response.code == 201){
                runOnUiThread{
                    Toast.makeText(this@LoginActivity,
                        "Successfully registered", Toast.LENGTH_SHORT).show()
                }

                var userid = response.headers["location"]!!.split("/").takeLast(1)[0]



                getlogin(username,pass)

                //Okhttp(name,pass,userid.toInt())
            }else{}

        }
    }

    private fun getlogin(name:String,pass:String){
        var client = OkHttpClient()

        println(name+"--------------"+pass)

        val credential = Credentials.basic(name, pass)

        val request = Request.Builder()
            .url(requestURL+"login")
            .header("Authorization",credential)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful){
                        println("Unexpected code $response")
                        runOnUiThread{
                            Toast.makeText(this@LoginActivity, "Username or Password incorrect", Toast.LENGTH_SHORT).show()
                        }
                    }

                    if (response.code == 200){
                        var json = JSONObject(response.body!!.string())
                        var userID = json["id"] as Int
                        Okhttp(name,pass,userID)
                    }
                }
            }
        })

    }


    private fun Okhttp(nameStr: String, passStr: String,id:Int) {
        run(nameStr, passStr,id)
    }

    fun run(nameStr: String, passStr: String,id:Int) {
        println("=========================================")
        //http://10.0.2.2:5000/match/1 //android simulator should use 10.0.2.2 replace 127.0.0.1
        val request = Request.Builder()
            .url(requestURL+"user/$id")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")

                    val json = JSONObject(response.body!!.string())
                    user = json.toString()

                    getToken(nameStr,passStr)

                    println("Password correct")
                }
            }
        })
    }

    private fun getToken(name: String, pass: String){
        var client = OkHttpClient()


        val credential = Credentials.basic(name, pass)

        val request = Request.Builder()
            .url(requestURL+"token")
            .header("Authorization",credential)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful){
                        println("Unexpected code $response")
                        runOnUiThread{
                            Toast.makeText(this@LoginActivity, "Username or Password incorrect", Toast.LENGTH_SHORT).show()
                        }
                    }

                    if (response.code == 200){
                        var json = JSONObject(response.body!!.string())
                        token = json["token"] as String
                        print("==========================================${token}")
                    }

                    val myIntent = Intent(applicationContext, MainActivity::class.java)
                    //return user json
                    myIntent.putExtra("user",user)
                    myIntent.putExtra("token",token)
                    startActivityForResult(myIntent, 0)
                    finish()
                }
            }
        })
    }




    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        val myIntent = Intent(applicationContext, MainActivity::class.java)
        startActivityForResult(myIntent, 0)
        finish()
        return true
    }
}

