// Copyright 2010 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"math/rand"
	"net"
	"net/http"
	"regexp"
	"strconv"
)

var (
	addr = flag.Bool("addr", false, "find open address and print to final-port.txt")
)

type Question struct {
	Q    string
	Q_id int
}

func (r Question) String() (s string) {
	b, err := json.Marshal(r)
	if err != nil {
		s = ""
		return
	}
	s = string(b)
	return
}

func getRandomQuestion() Question {
	qs := []Question{{"Va a A sacar mas votos que B?", 1}, {"Va a C superar el 10%?", 2}, {"Va a D superar a B y no a C?", 3}}
	return qs[rand.Intn(len(qs))]
}

func loadQuestion() (*Question, error) {
	q := getRandomQuestion()
	return &q, nil
}

func getHandler(w http.ResponseWriter, r *http.Request) {
	q, err := loadQuestion()
	if err != nil {
		return
	}
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprint(w, q)

}

func respondHandler(w http.ResponseWriter, r *http.Request, id int, response bool) {
	// Store response
	/*
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	*/
	http.Redirect(w, r, "/get", http.StatusFound)
}

var templates = template.Must(template.ParseFiles("index.html"))

func renderTemplate(w http.ResponseWriter, tmpl string, q *Question) {
	err := templates.ExecuteTemplate(w, tmpl+".html", q)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

var validGetPath = regexp.MustCompile("^/get/$")

func makeGetHandler(fn func(http.ResponseWriter, *http.Request)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		m := validGetPath.FindStringSubmatch(r.URL.Path)
		if m == nil {
			http.NotFound(w, r)
			return
		}
		fn(w, r)
	}
}

var validRespondPath = regexp.MustCompile("^/respond/([0-9]+)/([0-9]+)/([NY])$")

func makeRespondHandler(fn func(http.ResponseWriter, *http.Request, int, bool)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		m := validRespondPath.FindStringSubmatch(r.URL.Path)
		if m == nil {
			http.NotFound(w, r)
			return
		}
		fmt.Println(m)
		//uuid, _ := strconv.Atoi(m[1])
		q_id, _ := strconv.Atoi(m[2])
		if !((m[3] == "Y") || (m[3] == "N")) {
			http.Error(w, "Error en respuesta", 301)
			return
		}
		resp := false
		if m[3] == "Y" {
			resp = true
		}
		fn(w, r, q_id, resp)
	}
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	uuid := struct{ UUID int32 }{rand.Int31()}
	err := templates.ExecuteTemplate(w, "index.html", uuid)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
func makeIndexHandler(fn func(http.ResponseWriter, *http.Request)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		fn(w, r)
	}
}

func main() {
	flag.Parse()
	http.HandleFunc("/get/", makeGetHandler(getHandler))
	http.HandleFunc("/respond/", makeRespondHandler(respondHandler))

	http.Handle("/images/", http.StripPrefix("/images/", http.FileServer(http.Dir("./images/"))))
	http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("./css/"))))
	http.HandleFunc("/", makeIndexHandler(indexHandler))
	if *addr {
		l, err := net.Listen("tcp", "127.0.0.1:0")
		if err != nil {
			log.Fatal(err)
		}
		err = ioutil.WriteFile("final-port.txt", []byte(l.Addr().String()), 0644)
		if err != nil {
			log.Fatal(err)
		}
		s := &http.Server{}
		s.Serve(l)
		return
	}

	http.ListenAndServe(":8080", nil)
}
