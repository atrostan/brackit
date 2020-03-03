package com.example.d1.tournament

import android.app.Activity
import android.content.Intent
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.view.MenuItem
import android.view.View
import android.widget.ListView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.d1.BracketList
import com.example.d1.HomeList
import com.example.d1.MainActivity
import com.example.d1.R
import com.example.d1.dao.Match
import com.example.d1.network.GetBracket
import com.google.gson.Gson
import com.google.gson.JsonObject
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException


class TournamentActivity : AppCompatActivity(){

    val requestURL = "http://192.168.0.33:5000/api/"
    var userString = "nouser"
    var client = OkHttpClient()
    var currentRound = 0
    var totalRounds:Int = 0
    lateinit var preText:TextView
    lateinit var nextText:TextView
    lateinit var roundText:TextView
    var TournamentId = 0
    var realRound = 0

     var date:ArrayList<String> = arrayListOf()
     var score: ArrayList<String> = arrayListOf()
     var u1: ArrayList<Int> = arrayListOf()
     var u2:ArrayList<Int> = arrayListOf()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.tournament_homepage)

        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT

        if (intent.hasExtra("user")){
            userString = intent.getStringExtra("user")
        }

        preText = findViewById(R.id.last_round)
        nextText = findViewById(R.id.next_round)
        roundText = findViewById(R.id.current_round)

        roundText.text = "Round ${currentRound+1}"

        if(currentRound == 0){
            preText.visibility = View.INVISIBLE
        }


        val newString: String?
        newString = if (savedInstanceState == null) {
            val extras = intent.extras
            extras?.getString("STRING_I_NEED")
        } else {
            savedInstanceState.getSerializable("STRING_I_NEED") as String?
        }

        if (intent.hasExtra("tId")){
            var a = intent.getStringExtra("tId")
            TournamentId = a.toInt()
            println("-------------------$TournamentId in TournamentActivity")
            getTournament(TournamentId)
        }else{
            getTournament(1)
        }



        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }

    private fun getTournament(id: Int) {
        val request = Request.Builder()
            .url(requestURL+"tournament/"+ "$id")
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

                    getBracket(bid)

                }
            }
        })
    }

    private fun getBracket(id: Int) {
        val request = Request.Builder()
            .url(requestURL+"bracket/"+ "$id")
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
                 //   var text = findViewById<TextView>(R.id.name)
                    val json = JSONObject(response.body!!.string())

                    var rounds = json["rounds"] as JSONArray

                    realRound = rounds.getInt(0)

                    getRound(realRound)

                    //println(roundsList)
                    totalRounds = rounds.length()

                    println("=========================================")
                //    text.text = "Response: "+json + "   "+ rounds + " "

                }
            }
        })
    }

    private fun getRound(id: Int):JSONObject {

        clearBracket()

        var json:JSONObject = JSONObject()
        //var matchList:ArrayList<Match> = ArrayList()

        val request = Request.Builder()
            .url(requestURL+"round/$id")
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
                    //var text = findViewById<TextView>(R.id.name)
                    json = JSONObject(response.body!!.string())
                    //roundsList.add(json)

                    var matchList:ArrayList<Match> = ArrayList()

                    var matchs = json["matches"] as JSONArray

                    for(i in 0 until matchs.length()){
                        println("--------${matchs.getInt(i)} real match id--------")

                        getMatch(matchs.getInt(i))
                    }





                    println("====================getRound=====================")
                    println(date+"------------date")
                    println(score+"------------date")
                    println(u1+"------------date")
                    println(u2+"------------date")

                    runOnUiThread {
                        var listAdapter = BracketList(this@TournamentActivity,date,u1,score,u2)
                        listAdapter.notifyDataSetChanged()
                        val list = findViewById<ListView>(R.id.list_tournament)
                        list.adapter = listAdapter
                    }



                }
            }
        })

        return json
    }

    private fun getMatch(id:Int){
        val client = OkHttpClient()
        val request = Request.Builder()
            .url(requestURL+"match/$id")
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")

            var a = response.body!!.string()

            var gson = Gson()
            var matchOb = gson.fromJson(a,Match::class.java)

            setBracket("dateTemp","scoreTemp",matchOb.u1,matchOb.u2)

        }


    }

    private fun setBracket(date1:String,score1:String,u11:Int,u21:Int){
        date.add(date1)
        score.add(score1)
        u1.add(u11)
        u2.add(u21)
    }

    private fun clearBracket(){
        date = arrayListOf()
        score = arrayListOf()
        u1= arrayListOf()
        u2 = arrayListOf()
    }


    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        val myIntent = Intent(applicationContext, MainActivity::class.java)
        myIntent.putExtra("user",userString)
        myIntent.putExtra("tId",TournamentId.toString())
        startActivityForResult(myIntent, 0)
        finish()
        return true
    }

    fun onPrevClick(v:View){
        if (preText.visibility == View.VISIBLE){
           // var text = findViewById<TextView>(R.id.name)


            if (currentRound -1 >=0){
                currentRound-=1
                roundText.text = "Round ${currentRound+1}"
            }

            if(currentRound == 0){
                preText.visibility = View.INVISIBLE
            }
            if(currentRound != totalRounds-1){
                nextText.visibility = View.VISIBLE
            }

            realRound-=1
            println("--------$realRound--------")

            var round = getRound(realRound)

        }

    }

    fun onNextClick(v:View){
        if(nextText.visibility == View.VISIBLE){
           // var text = findViewById<TextView>(R.id.name)
            //text.setText("Next")
            if (currentRound + 1 < totalRounds){
                currentRound+=1
                roundText.text = "Round ${currentRound+1}"
            }

            if(currentRound != 0){
                preText.visibility = View.VISIBLE
            }
            if(currentRound == totalRounds-1){
                nextText.visibility = View.INVISIBLE
            }

            realRound+=1
            println("--------$realRound--------")
            var round = getRound(realRound)

//            var listAdapter = BracketList(this,date,u1,score,u2)
//            val list = findViewById<ListView>(R.id.list_tournament)
//            list.adapter = listAdapter

           // text.setText("Previous+ "+ date)
        }

    }



}
