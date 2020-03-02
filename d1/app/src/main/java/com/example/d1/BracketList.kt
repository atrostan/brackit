package com.example.d1

import android.app.Activity
import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.ImageView
import android.widget.TextView

class BracketList (private val context: Activity,
                   private val date: ArrayList<String>, private val u1: ArrayList<Int>,
                   private val score: ArrayList<String>,private val u2:ArrayList<Int>
) : ArrayAdapter<String>(context, R.layout.bracket_list_single, date) {
    override fun getView(position: Int, view: View?, parent: ViewGroup): View {
        val inflater = context.layoutInflater
        val rowView = inflater.inflate(R.layout.bracket_list_single, null, true)
//        val txtTitle = rowView.findViewById<View>(R.id.txt) as TextView
//        val imageView = rowView.findViewById<View>(R.id.img) as ImageView
//        txtTitle.text = web[position]
//        imageView.setImageResource(imageId[position])
//        return rowView
        val dateTitle = rowView.findViewById<View>(R.id.date) as TextView
        val u1Title = rowView.findViewById<View>(R.id.u1) as TextView
        val scoreTitle = rowView.findViewById<View>(R.id.score) as TextView
        val u2Title = rowView.findViewById<View>(R.id.u2) as TextView
        dateTitle.text = date[position]
        u1Title.text = u1[position].toString()
        u2Title.text = u2[position].toString()
        scoreTitle.text = score[position]

        return rowView

    }
}
//
