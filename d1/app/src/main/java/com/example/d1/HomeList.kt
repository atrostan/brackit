package com.example.d1

import android.app.Activity
import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.ImageView
import android.widget.TextView

class HomeList(
    private val context: Activity,
    private val web: ArrayList<String>, private val imageId: ArrayList<Int>
) : ArrayAdapter<String>(context, R.layout.home_list_single, web) {


    override fun getView(position: Int, view: View?, parent: ViewGroup): View {
        val inflater = context.layoutInflater
        val rowView = inflater.inflate(R.layout.home_list_single, null, true)
        val txtTitle = rowView.findViewById<View>(R.id.txt) as TextView
        val imageView = rowView.findViewById<View>(R.id.img) as ImageView
        txtTitle.text = web[position]
        imageView.setImageResource(imageId[position])
        return rowView

    }
}
