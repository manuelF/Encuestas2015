package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/fzzy/radix/redis"
	"html/template"
	"io/ioutil"
	"log"
	"math"
	"math/rand"
	"net"
	"net/http"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

var (
	addr = flag.Bool("addr", false, "find open address and print to final-port.txt")
	//qs            = []Question{{"Va a A sacar mas votos que B?", 1}, {"Va a C superar el 10%?", 2}, {"Va a D superar a B y no a C?", 3}}
	qs            = []Question{}
	questionStats = []QuestionStats{}
	qidqs         = map[int]*QuestionStats{}
	qidq          = map[int]Question{}
	c             = &redis.Client{}
	formats       = []string{"%v sacara mas votos que %v?", "%v sacara mas del %v porciento de votos?",
		"%v sacara menos del %v porciento	de los votos?", "Algun candidato sacara mas del %v porciento de los votos?",
		"El ganador, le sacara al menos %v porciento al segundo?", "Habra al menos %v candidatos con mas del %v porciento cada uno?"}
)

type Question struct {
	id    int
	qtype int
	arg1  int
	arg2  int
}

type QuestionStats struct {
	Q_id     int
	Positive int
	Negative int
}

func (q QuestionStats) Ratio() float64 {
	den := (float64(q.Positive) + float64(q.Negative))
	// If there never was such a question, it is more interesting to make it asap
	if den == 0 {
		return 0.5
	}
	return float64(q.Positive) / den
}

func distanceToHalf(f float64) float64 {
	return math.Abs(0.5 - f)
}

func loadQuestions() {
	// Parse the questions file
	// Format: <qnumber> <qtype> <arg1> <arg2>
	b, err := ioutil.ReadFile("engine/questions.txt")
	if err != nil {
		panic(err)
	}
	reader := bufio.NewReader(bytes.NewBuffer(b))
	for {
		str, _err := reader.ReadString('\n')
		if _err != nil {
			break
		}
		qparts := strings.Split(strings.TrimSpace(str), " ")
		qid, _ := strconv.Atoi(qparts[0])
		qtype, _ := strconv.Atoi(qparts[1])
		arg1, _ := strconv.Atoi(qparts[2])
		arg2 := 0
		if len(qparts) > 3 {
			arg2, _ = strconv.Atoi(qparts[3])
		}
		tmp := Question{qid, qtype, arg1, arg2}
		qs = append(qs, tmp)
		questionStats = append(questionStats, QuestionStats{qid, 0, 0})
	}
}

// By is the type of a "less" function that defines the ordering of its Planet arguments.
type By func(q1, q2 *QuestionStats) bool

// Sort is a method on the function type, By, that sorts the argument slice according to the function.
func (by By) Sort(questions []QuestionStats) {
	ps := &questionSorter{
		qs: questions,
		by: by, // The Sort method's receiver is the function (closure) that defines the sort order.
	}
	sort.Sort(ps)
}

// questionSorter joins a By function and a slice of questions to be sorted.
type questionSorter struct {
	qs []QuestionStats
	by By // Closure used in the Less method.
}

// Len is part of sort.Interface.
func (s *questionSorter) Len() int {
	return len(s.qs)
}

// Swap is part of sort.Interface.
func (s *questionSorter) Swap(i, j int) {
	s.qs[i], s.qs[j] = s.qs[j], s.qs[i]
}

// Less is part of sort.Interface. It is implemented by calling the "by" closure in the sorter.
func (s *questionSorter) Less(i, j int) bool {
	return s.by(&s.qs[i], &s.qs[j])
}

func (r Question) String() (s string) {
	data := struct {
		Q    string
		Q_id int
	}{
		r.PrettyPrint(),
		r.id,
	}
	b, err := json.Marshal(data)
	if err != nil {
		s = ""
		return
	}
	s = string(b)
	return
}

func (r Question) PrettyPrint() string {
	if r.qtype == 1 || r.qtype == 2 || r.qtype == 3 || r.qtype == 6 {
		return fmt.Sprintf(formats[r.qtype-1], r.arg1, r.arg2)
	} else {
		return fmt.Sprintf(formats[r.qtype-1], r.arg1)
	}
}

func getQuestion() Question {
	tightestRatio := func(q1, q2 *QuestionStats) bool {
		return distanceToHalf(q1.Ratio()) < distanceToHalf(q2.Ratio())
	}
	//fmt.Println(questionStats)
	if rand.Intn(2) == 0 {
		By(tightestRatio).Sort(questionStats)
		q := qidq[questionStats[0].Q_id]
		return q
	} else {
		return qidq[rand.Intn(len(qs))+1]
	}
}

func getHandler(w http.ResponseWriter, r *http.Request) {
	q := getQuestion()
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprint(w, q)
}

func respondHandler(w http.ResponseWriter, r *http.Request, uuid int, id int, response bool) {
	// Store response in REDIS
	// go redis push q:id:y -> uuid
	st := "N"
	if response {
		st = "Y"
	}

	c.Cmd("SADD", fmt.Sprintf("q:%vr:%v", id, st), uuid)
	if response {
		qidqs[id].Positive++
	} else {
		qidqs[id].Negative++
	}
	http.Redirect(w, r, "/get/", http.StatusFound)
}

var templates = template.Must(template.ParseFiles("index.html"))

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

// Format of response is /respond/<user_id>/<question_number>/<Yes/No>
var validRespondPath = regexp.MustCompile("^/respond/([0-9]+)/([0-9]+)/([NY])$")

func makeRespondHandler(fn func(http.ResponseWriter, *http.Request, int, int, bool)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		m := validRespondPath.FindStringSubmatch(r.URL.Path)
		if m == nil {
			http.NotFound(w, r)
			return
		}
		fmt.Println(m)
		uuid, _ := strconv.Atoi(m[1])
		q_id, _ := strconv.Atoi(m[2])
		if !((m[3] == "Y") || (m[3] == "N")) {
			http.Error(w, "Error en respuesta", 301)
			return
		}
		resp := false
		if m[3] == "Y" {
			resp = true
		}
		fn(w, r, uuid, q_id, resp)
	}
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	uuid := struct{ UUID int32 }{rand.Int31()}
	err := templates.ExecuteTemplate(w, "index.html", uuid)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func InitializeMaps() {
	loadQuestions()
	for index, q := range qs {
		qidq[q.id] = q
		qidqs[q.id] = &questionStats[index]
	}
}

func main() {
	flag.Parse()
	http.HandleFunc("/get/", makeGetHandler(getHandler))
	http.HandleFunc("/respond/", makeRespondHandler(respondHandler))
	http.HandleFunc("/", indexHandler)
	http.Handle("/images/", http.StripPrefix("/images/", http.FileServer(http.Dir("./images/"))))
	http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("./css/"))))

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
	var err error
	c, err = redis.Dial("tcp", "localhost:6379")

	if err != nil {
		log.Fatal(err)
	}
	InitializeMaps()
	http.ListenAndServe(":8080", nil)
}
