package com.example.d1.network

import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.URL

class OKHttpNetwork(var URL:String,var client:OkHttpClient) {

    private fun getTournament(id: Int) {
        val request = Request.Builder()
            .url( URL+"tournament/"+ "$id")
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
                    //     var text = findViewById<TextView>(R.id.name)
                    val json = JSONObject(response.body!!.string())

                    var brackets = json["brackets"] as JSONArray
                    var bid = brackets.getInt(0)

                    println("=========================================")
                    //  text.text = "Response: "+json + "   "+ brackets.javaClass.name

                }
            }
        })
    }
}