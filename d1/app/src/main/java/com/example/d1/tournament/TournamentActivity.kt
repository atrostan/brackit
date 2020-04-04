package com.example.d1.tournament

import android.content.Intent
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.view.MenuItem
import android.view.View
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.d1.BracketList
import com.example.d1.MainActivity
import com.example.d1.R
import com.example.d1.dao.*
import com.google.gson.Gson
import okhttp3.*
import java.io.IOException


class TournamentActivity : AppCompatActivity(){

    val requestURL = "http://10.0.2.2:5000/api/"
    //val requestURL = "http://172.20.10.2:5000/api/"
    var userString = "nouser"
    var client = OkHttpClient()
    var currentRound = 0
    var totalRounds:Int = 0
    lateinit var preText:TextView
    lateinit var nextText:TextView
    lateinit var roundText:TextView
    var TournamentId = 0
    var realRound = 0
    var realRound_loser = 0
    var u1ID = 0
    var u2ID = 0
    var winnersLosersRounds:WinnersLosersRounds? = null
    var tournamentfull:TournamentFull?=null
    var TOKEN = ""
    var EDIT = ""
    lateinit var users:List<UserX>


    var date:ArrayList<String> = arrayListOf()
    var score: ArrayList<String> = arrayListOf()
    var u1: ArrayList<String> = arrayListOf()
    var u2:ArrayList<String> = arrayListOf()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.tournament_homepage)

        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT

        if (intent.hasExtra("user")){

            userString = intent.getStringExtra("user")
        }
        if (intent.hasExtra("token")){
            TOKEN = intent.getStringExtra("token")
        }
        if (intent.hasExtra("edit")){
            EDIT = intent.getStringExtra("edit")
        }

        preText = findViewById(R.id.last_round)
        nextText = findViewById(R.id.next_round)
        roundText = findViewById(R.id.current_round)

        roundText.text = "Round ${currentRound+1}"

        if(currentRound == 0){
            preText.visibility = View.INVISIBLE
        }


        if (intent.hasExtra("tId")){
            var a = intent.getStringExtra("tId")
            TournamentId = a.toInt()
            println("-------------------$TournamentId in TournamentActivity")
            getFullTournamnet(TournamentId)
            //getTournament(TournamentId)
        }else{
            TournamentId = 0
            getFullTournamnet(1)
            //getTournament(1)
        }

        if (EDIT == "EDIT"){
            var list_tournament = findViewById<ListView>(R.id.list_tournament)
            list_tournament.setOnItemClickListener { parent, view, position, id ->
                if(u1[+position] != "null" && u1[+position] != "Losers"){
                    val intent = intent.setClassName(this,"com.example.d1.tournament.EditScoreActivity")
                    for (u in users){
                        if (u1[+position] == u.username){
                            u1ID = u.id
                        }
                        if (u2[+position] == u.username){
                            u2ID = u.id
                        }
                        println("----------${u1[+position]}---$u1ID-----------------------${u2[+position]}---$u2ID-----------------------")
                    }
                    intent.putExtra("user",userString)
                    intent.putExtra("token",TOKEN)
                    intent.putExtra("mid",date[+position])
                    intent.putExtra("u1ID",u1ID.toString())
                    intent.putExtra("u2ID",u2ID.toString())
                    //intent.putExtra("mId",)
                    startActivity(intent)
                    finish()
                }

                Toast.makeText(this, "You Cannot edit this match", Toast.LENGTH_SHORT).show()
            }
        }







        //next button click
        nextText.setOnClickListener{
            if(nextText.visibility == View.VISIBLE){
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

                clearBracket()
                getFullTournamnet(TournamentId)

                println("realRound-------------------$realRound")
                println("realRound_loser-------------------$realRound_loser")
            }
        }

        //prev button click
        preText.setOnClickListener{
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

                clearBracket()
                getFullTournamnet(TournamentId)


                println("realRound-------------------$realRound")
                println("realRound_loser-------------------$realRound_loser")
            }
        }

        //navigate back
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }

    fun getWinnerLoserRounds(id:Int){
        val request = Request.Builder()
            .url(requestURL+"bracket/$id/winners_losers_rounds")
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
                    val json = response.body!!.string()

                    var gson = Gson()
                    winnersLosersRounds = gson.fromJson(json,WinnersLosersRounds::class.java)
                    var losersRound = winnersLosersRounds!!.losers_rounds
                    var winnersRound = winnersLosersRounds!!.winners_rounds
                    totalRounds = winnersLosersRounds!!.winners_rounds.size

                    var bracket = tournamentfull!!.brackets[0]

                    for (r:Round in bracket.rounds){
                        //set winner
                        if (r.id == winnersRound[currentRound].id){
                            for (m:Matche in r.matches){
                                if (m.u1 == null){
                                    u1.add("null")
                                }else{
                                    u1.add(m.u1.username)
                                }
                                if (m.u2 == null){
                                    u2.add("null")
                                }else{
                                    u2.add(m.u2.username)
                                }
                                if (m.user_1_score == null && m.user_2_score == null){
                                    score.add("0 : 0")
                                }else{
                                    score.add("${m.user_1_score} : ${m.user_2_score}")
                                }
                                date.add("${m.id}")

                            }
                        }
                    }

                    if (currentRound+1 < losersRound.size){
                        setBracket("","Bracket","Losers","")
                        for (r:Round in bracket.rounds){
                            //set loser
                            if (r.id == losersRound[currentRound].id){
                                for (m:Matche in r.matches){
                                    if (m.u1 == null){
                                        u1.add("null")
                                    }else{
                                        u1.add(m.u1.username)
                                    }
                                    if (m.u2 == null){
                                        u2.add("null")
                                    }else{
                                        u2.add(m.u2.username)
                                    }
                                    if (m.user_1_score == null && m.user_2_score == null){
                                        score.add("0 : 0")
                                    }else{
                                        score.add("${m.user_1_score} : ${m.user_2_score}")
                                    }
                                    date.add("${m.id}")

                                }
                            }
                        }
                    }



                    runOnUiThread {
                        var listAdapter = BracketList(this@TournamentActivity,date,u1,score,u2)
                        listAdapter.notifyDataSetChanged()
                        val list = findViewById<ListView>(R.id.list_tournament)
                        list.adapter = listAdapter
                    }



                    println(winnersLosersRounds!!.losers_rounds)
                    println(winnersLosersRounds!!.winners_rounds)

                }
            }
        })
    }

    fun getFullTournamnet(id:Int){
        val request = Request.Builder()
            .url(requestURL+"tournament/$id/full")
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
                    val json = response.body!!.string()

                    var gson = Gson()
                    tournamentfull = gson.fromJson(json,TournamentFull::class.java)
                    users = tournamentfull!!.brackets[0].users

                    getWinnerLoserRounds(id)


                }
            }
        })
    }


    private fun setBracket(date1:String,score1:String,u11:String,u21:String){
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
        myIntent.putExtra("token",TOKEN)
        //myIntent.putExtra("tId",TournamentId.toString())
        startActivityForResult(myIntent, 0)
        finish()
        return true
    }





}

