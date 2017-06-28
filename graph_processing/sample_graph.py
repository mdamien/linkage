X = """0 1 1
0 2 1
3 4 1
3 5 1
3 6 1
3 7 1
3 8 1
4 5 1
4 6 1
4 7 1
4 8 1
5 6 1
5 7 1
5 8 1
6 7 1
6 8 1
7 8 1
0 9 1
0 10 1
9 10 1
0 11 1
0 4 1
1 0 1
1 12 1
1 13 1
0 12 1
0 13 1
12 13 1
6 3 1
6 4 1
6 5 1
7 4 1
7 5 1
14 15 1
14 0 1
15 0 1
0 16 1
2 16 1
0 17 1
0 18 1
17 18 1
1 19 1
0 19 1
12 19 1
0 15 1
0 20 1
15 20 1
0 21 1
0 22 1
21 22 1
0 23 1
18 23 1
0 24 1
24 4 1
0 25 1
26 0 1
26 18 1
0 27 1
0 28 1
0 29 1
0 30 1
27 28 1
27 29 1
27 15 1
27 30 1
28 29 1
28 15 1
28 30 1
29 15 1
29 30 1
15 30 1
0 31 1
18 31 1
0 32 1
32 23 1
0 33 1
0 34 1
33 34 1
0 14 1
21 14 1
15 35 1
20 0 1
20 35 1
0 35 1
0 36 1
36 23 1
36 32 1
23 32 1
9 4 1
17 0 1
37 38 1
37 0 1
37 4 1
37 39 1
38 0 1
38 4 1
38 39 1
0 39 1
4 39 1
18 0 1
0 40 1
40 18 1
41 0 1
41 42 1
41 43 1
0 42 1
0 43 1
42 43 1
4 0 1
4 18 1
4 44 1
4 45 1
4 46 1
0 44 1
0 45 1
0 46 1
18 44 1
18 45 1
18 46 1
44 45 1
44 46 1
45 46 1
46 46 0
"""
tdm = """0 0 1
1 0 1
2 0 1
3 0 1
4 1 1
5 1 1
6 1 1
7 1 1
8 2 4
9 2 1
10 2 1
11 2 1
12 2 1
13 2 1
14 2 1
15 2 1
16 2 1
17 2 1
18 2 1
19 2 1
20 2 1
21 2 1
22 2 1
8 3 4
9 3 1
10 3 1
11 3 1
12 3 1
13 3 1
14 3 1
15 3 1
16 3 1
17 3 1
18 3 1
19 3 1
20 3 1
21 3 1
22 3 1
8 4 4
9 4 1
10 4 1
11 4 1
12 4 1
13 4 1
14 4 1
15 4 1
16 4 1
17 4 1
18 4 1
19 4 1
20 4 1
21 4 1
22 4 1
8 5 4
9 5 1
10 5 1
11 5 1
12 5 1
13 5 1
14 5 1
15 5 1
16 5 1
17 5 1
18 5 1
19 5 1
20 5 1
21 5 1
22 5 1
8 6 4
9 6 1
10 6 1
11 6 1
12 6 1
13 6 1
14 6 1
15 6 1
16 6 1
17 6 1
18 6 1
19 6 1
20 6 1
21 6 1
22 6 1
8 7 4
9 7 1
10 7 1
11 7 1
12 7 1
13 7 1
14 7 1
15 7 1
16 7 1
17 7 1
18 7 1
19 7 1
20 7 1
21 7 1
22 7 1
8 8 4
9 8 1
10 8 1
11 8 1
12 8 1
13 8 1
14 8 1
15 8 1
16 8 1
17 8 1
18 8 1
19 8 1
20 8 1
21 8 1
22 8 1
8 9 4
9 9 1
10 9 1
11 9 1
12 9 1
13 9 1
14 9 1
15 9 1
16 9 1
17 9 1
18 9 1
19 9 1
20 9 1
21 9 1
22 9 1
8 10 4
9 10 1
10 10 1
11 10 1
12 10 1
13 10 1
14 10 1
15 10 1
16 10 1
17 10 1
18 10 1
19 10 1
20 10 1
21 10 1
22 10 1
8 11 4
9 11 1
10 11 1
11 11 1
12 11 1
13 11 1
14 11 1
15 11 1
16 11 1
17 11 1
18 11 1
19 11 1
20 11 1
21 11 1
22 11 1
8 12 4
9 12 1
10 12 1
11 12 1
12 12 1
13 12 1
14 12 1
15 12 1
16 12 1
17 12 1
18 12 1
19 12 1
20 12 1
21 12 1
22 12 1
8 13 4
9 13 1
10 13 1
11 13 1
12 13 1
13 13 1
14 13 1
15 13 1
16 13 1
17 13 1
18 13 1
19 13 1
20 13 1
21 13 1
22 13 1
8 14 4
9 14 1
10 14 1
11 14 1
12 14 1
13 14 1
14 14 1
15 14 1
16 14 1
17 14 1
18 14 1
19 14 1
20 14 1
21 14 1
22 14 1
8 15 4
9 15 1
10 15 1
11 15 1
12 15 1
13 15 1
14 15 1
15 15 1
16 15 1
17 15 1
18 15 1
19 15 1
20 15 1
21 15 1
22 15 1
8 16 4
9 16 1
10 16 1
11 16 1
12 16 1
13 16 1
14 16 1
15 16 1
16 16 1
17 16 1
18 16 1
19 16 1
20 16 1
21 16 1
22 16 1
23 17 1
7 17 1
24 17 1
12 17 1
25 17 1
26 17 1
27 17 1
28 17 1
29 17 1
30 17 1
23 18 1
7 18 1
24 18 1
12 18 1
25 18 1
26 18 1
27 18 1
28 18 1
29 18 1
30 18 1
23 19 1
7 19 1
24 19 1
12 19 1
25 19 1
26 19 1
27 19 1
28 19 1
29 19 1
30 19 1
31 20 1
6 20 1
32 20 1
33 20 1
34 20 1
0 20 1
5 20 1
35 20 1
36 20 1
37 21 1
38 21 1
39 21 1
40 21 1
41 21 1
42 21 1
43 21 1
44 21 1
45 21 1
1 22 1
39 22 1
7 22 1
46 22 1
47 22 1
0 22 1
48 22 1
49 22 1
3 22 1
1 23 1
39 23 1
7 23 1
46 23 1
47 23 1
0 23 1
48 23 1
49 23 1
3 23 1
1 24 1
39 24 1
7 24 1
46 24 1
47 24 1
0 24 1
48 24 1
49 24 1
3 24 1
1 25 1
39 25 1
7 25 1
46 25 1
47 25 1
0 25 1
48 25 1
49 25 1
3 25 1
1 26 1
39 26 1
7 26 1
46 26 1
47 26 1
0 26 1
48 26 1
49 26 1
3 26 1
1 27 1
39 27 1
7 27 1
46 27 1
47 27 1
0 27 1
48 27 1
49 27 1
3 27 1
50 28 1
13 28 1
39 28 1
51 28 1
12 28 1
0 28 2
25 28 1
52 28 1
53 28 1
3 28 1
50 29 1
13 29 1
39 29 1
51 29 1
12 29 1
0 29 2
25 29 1
52 29 1
53 29 1
3 29 1
50 30 1
13 30 1
39 30 1
51 30 1
12 30 1
0 30 2
25 30 1
52 30 1
53 30 1
3 30 1
50 31 1
13 31 1
39 31 1
51 31 1
12 31 1
0 31 2
25 31 1
52 31 1
53 31 1
3 31 1
50 32 1
13 32 1
39 32 1
51 32 1
12 32 1
0 32 2
25 32 1
52 32 1
53 32 1
3 32 1
54 33 1
1 33 1
55 33 1
56 33 1
57 33 1
58 33 1
54 34 1
1 34 1
55 34 1
56 34 1
57 34 1
58 34 1
54 35 1
1 35 1
55 35 1
56 35 1
57 35 1
58 35 1
59 36 1
60 36 1
61 36 1
0 36 1
62 36 1
3 36 1
59 37 1
60 37 1
61 37 1
0 37 1
62 37 1
3 37 1
1 38 1
6 38 1
51 38 1
25 38 1
5 38 1
63 38 1
64 38 1
65 38 1
1 39 1
6 39 1
51 39 1
25 39 1
5 39 1
63 39 1
64 39 1
65 39 1
1 40 1
6 40 1
51 40 1
25 40 1
5 40 1
63 40 1
64 40 1
65 40 1
66 41 1
67 41 1
28 41 1
60 41 1
68 41 1
69 41 1
13 41 1
70 41 1
71 41 1
72 41 1
66 42 1
67 42 1
28 42 1
60 42 1
68 42 1
69 42 1
13 42 1
70 42 1
71 42 1
72 42 1
66 43 1
67 43 1
28 43 1
60 43 1
68 43 1
69 43 1
13 43 1
70 43 1
71 43 1
72 43 1
7 44 1
73 44 1
74 44 1
47 44 1
75 44 1
76 44 1
77 44 1
7 45 1
73 45 1
74 45 1
47 45 1
75 45 1
76 45 1
77 45 1
7 46 1
73 46 1
74 46 1
47 46 1
75 46 1
76 46 1
77 46 1
55 47 1
1 47 1
78 47 1
79 47 1
80 47 1
81 47 1
25 47 1
30 47 1
82 47 1
83 47 1
55 48 1
1 48 1
78 48 1
79 48 1
80 48 1
81 48 1
25 48 1
30 48 1
82 48 1
83 48 1
55 49 1
1 49 1
78 49 1
79 49 1
80 49 1
81 49 1
25 49 1
30 49 1
82 49 1
83 49 1
8 50 2
84 50 1
85 50 1
12 50 1
16 50 1
14 50 1
22 50 1
86 50 1
8 51 2
84 51 1
85 51 1
12 51 1
16 51 1
14 51 1
22 51 1
86 51 1
87 52 1
88 52 1
41 52 1
42 52 1
25 52 2
43 52 1
87 53 1
88 53 1
41 53 1
42 53 1
25 53 2
43 53 1
1 54 1
89 54 1
90 54 1
5 54 1
75 54 1
76 54 1
77 54 1
0 55 1
91 55 1
92 55 1
40 55 1
93 55 1
1 55 1
5 55 1
94 55 1
46 55 1
6 55 1
3 55 1
0 56 1
91 56 1
92 56 1
40 56 1
93 56 1
1 56 1
5 56 1
94 56 1
46 56 1
6 56 1
3 56 1
95 57 1
6 57 1
25 57 1
96 57 1
82 57 1
97 57 1
98 57 1
99 57 1
30 57 1
95 58 1
6 58 1
25 58 1
96 58 1
82 58 1
97 58 1
98 58 1
99 58 1
30 58 1
95 59 1
6 59 1
25 59 1
96 59 1
82 59 1
97 59 1
98 59 1
99 59 1
30 59 1
95 60 1
6 60 1
25 60 1
96 60 1
82 60 1
97 60 1
98 60 1
99 60 1
30 60 1
95 61 1
6 61 1
25 61 1
96 61 1
82 61 1
97 61 1
98 61 1
99 61 1
30 61 1
95 62 1
6 62 1
25 62 1
96 62 1
82 62 1
97 62 1
98 62 1
99 62 1
30 62 1
95 63 1
6 63 1
25 63 1
96 63 1
82 63 1
97 63 1
98 63 1
99 63 1
30 63 1
95 64 1
6 64 1
25 64 1
96 64 1
82 64 1
97 64 1
98 64 1
99 64 1
30 64 1
95 65 1
6 65 1
25 65 1
96 65 1
82 65 1
97 65 1
98 65 1
99 65 1
30 65 1
95 66 1
6 66 1
25 66 1
96 66 1
82 66 1
97 66 1
98 66 1
99 66 1
30 66 1
95 67 1
6 67 1
25 67 1
96 67 1
82 67 1
97 67 1
98 67 1
99 67 1
30 67 1
95 68 1
6 68 1
25 68 1
96 68 1
82 68 1
97 68 1
98 68 1
99 68 1
30 68 1
95 69 1
6 69 1
25 69 1
96 69 1
82 69 1
97 69 1
98 69 1
99 69 1
30 69 1
95 70 1
6 70 1
25 70 1
96 70 1
82 70 1
97 70 1
98 70 1
99 70 1
30 70 1
29 71 1
12 71 1
100 71 1
0 71 1
101 71 1
102 71 1
103 71 1
104 71 1
29 72 1
12 72 1
100 72 1
0 72 1
101 72 1
102 72 1
103 72 1
104 72 1
6 73 1
105 73 1
0 73 1
5 73 1
106 73 1
3 73 1
6 74 1
105 74 1
0 74 1
5 74 1
106 74 1
3 74 1
12 75 1
12 76 1
12 77 1
8 78 2
107 78 1
10 78 1
108 78 1
109 78 1
110 78 1
15 78 1
17 78 1
111 78 1
112 78 1
113 78 1
114 78 1
8 79 2
107 79 1
10 79 1
108 79 1
109 79 1
110 79 1
15 79 1
17 79 1
111 79 1
112 79 1
113 79 1
114 79 1
115 80 1
3 80 1
73 80 1
89 80 1
43 80 1
116 80 1
77 80 1
117 80 1
118 80 1
119 80 1
75 80 1
120 80 1
115 81 1
3 81 1
73 81 1
89 81 1
43 81 1
116 81 1
77 81 1
117 81 1
118 81 1
119 81 1
75 81 1
120 81 1
115 82 1
3 82 1
73 82 1
89 82 1
43 82 1
116 82 1
77 82 1
117 82 1
118 82 1
119 82 1
75 82 1
120 82 1
115 83 1
3 83 1
73 83 1
89 83 1
43 83 1
116 83 1
77 83 1
117 83 1
118 83 1
119 83 1
75 83 1
120 83 1
121 84 1
122 84 1
106 84 1
123 84 2
1 84 1
121 85 1
122 85 1
106 85 1
123 85 2
1 85 1
121 86 1
122 86 1
106 86 1
123 86 2
1 86 1
121 87 1
122 87 1
106 87 1
123 87 2
1 87 1
8 88 1
124 88 1
125 88 1
126 88 1
127 88 1
128 88 1
129 88 1
130 88 1
15 88 1
85 88 1
17 88 1
131 88 1
132 88 1
86 88 1
34 89 1
133 89 1
51 89 1
134 89 1
12 89 1
25 89 1
135 89 1
63 89 1
65 89 1
136 90 1
137 90 1
138 90 1
139 90 1
25 90 1
140 90 1
141 90 1
142 90 1
143 90 1
136 91 1
137 91 1
138 91 1
139 91 1
25 91 1
140 91 1
141 91 1
142 91 1
143 91 1
136 92 1
137 92 1
138 92 1
139 92 1
25 92 1
140 92 1
141 92 1
142 92 1
143 92 1
136 93 1
137 93 1
138 93 1
139 93 1
25 93 1
140 93 1
141 93 1
142 93 1
143 93 1
136 94 1
137 94 1
138 94 1
139 94 1
25 94 1
140 94 1
141 94 1
142 94 1
143 94 1
136 95 1
137 95 1
138 95 1
139 95 1
25 95 1
140 95 1
141 95 1
142 95 1
143 95 1
136 96 1
137 96 1
138 96 1
139 96 1
25 96 1
140 96 1
141 96 1
142 96 1
143 96 1
136 97 1
137 97 1
138 97 1
139 97 1
25 97 1
140 97 1
141 97 1
142 97 1
143 97 1
136 98 1
137 98 1
138 98 1
139 98 1
25 98 1
140 98 1
141 98 1
142 98 1
143 98 1
8 99 1
144 99 1
10 99 1
145 99 1
40 99 1
12 99 1
13 99 1
146 99 1
14 99 1
16 99 1
147 99 1
22 99 1
86 99 1
148 100 1
7 100 1
149 100 1
47 100 1
150 100 1
22 100 1
151 100 1
152 100 1
148 101 1
7 101 1
149 101 1
47 101 1
150 101 1
22 101 1
151 101 1
152 101 1
153 102 1
154 102 1
155 102 1
0 102 1
156 102 1
125 102 1
157 102 1
158 102 1
159 102 1
160 102 1
161 102 1
114 102 1
162 102 1
153 103 1
154 103 1
155 103 1
0 103 1
156 103 1
125 103 1
157 103 1
158 103 1
159 103 1
160 103 1
161 103 1
114 103 1
162 103 1
153 104 1
154 104 1
155 104 1
0 104 1
156 104 1
125 104 1
157 104 1
158 104 1
159 104 1
160 104 1
161 104 1
114 104 1
162 104 1
153 105 1
154 105 1
155 105 1
0 105 1
156 105 1
125 105 1
157 105 1
158 105 1
159 105 1
160 105 1
161 105 1
114 105 1
162 105 1
153 106 1
154 106 1
155 106 1
0 106 1
156 106 1
125 106 1
157 106 1
158 106 1
159 106 1
160 106 1
161 106 1
114 106 1
162 106 1
153 107 1
154 107 1
155 107 1
0 107 1
156 107 1
125 107 1
157 107 1
158 107 1
159 107 1
160 107 1
161 107 1
114 107 1
162 107 1
39 108 1
51 108 1
12 108 1
0 108 1
25 108 1
52 108 1
163 108 1
3 108 1
39 109 1
51 109 1
12 109 1
0 109 1
25 109 1
52 109 1
163 109 1
3 109 1
39 110 1
51 110 1
12 110 1
0 110 1
25 110 1
52 110 1
163 110 1
3 110 1
39 111 1
51 111 1
12 111 1
0 111 1
25 111 1
52 111 1
163 111 1
3 111 1
39 112 1
51 112 1
12 112 1
0 112 1
25 112 1
52 112 1
163 112 1
3 112 1
39 113 1
51 113 1
12 113 1
0 113 1
25 113 1
52 113 1
163 113 1
3 113 1
39 114 1
51 114 1
12 114 1
0 114 1
25 114 1
52 114 1
163 114 1
3 114 1
39 115 1
51 115 1
12 115 1
0 115 1
25 115 1
52 115 1
163 115 1
3 115 1
39 116 1
51 116 1
12 116 1
0 116 1
25 116 1
52 116 1
163 116 1
3 116 1
39 117 1
51 117 1
12 117 1
0 117 1
25 117 1
52 117 1
163 117 1
3 117 1
39 118 1
51 118 1
12 118 1
0 118 1
25 118 1
52 118 1
163 118 1
3 118 1
39 119 1
51 119 1
12 119 1
0 119 1
25 119 1
52 119 1
163 119 1
3 119 1
39 120 1
51 120 1
12 120 1
0 120 1
25 120 1
52 120 1
163 120 1
3 120 1
39 121 1
51 121 1
12 121 1
0 121 1
25 121 1
52 121 1
163 121 1
3 121 1
"""
