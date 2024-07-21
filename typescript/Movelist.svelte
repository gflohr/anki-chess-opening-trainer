<chess-navigation>
	<button>&nbsp;&nbsp;=&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;|&lt;&lt;&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;&lt;&lt;&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;&gt;&gt;&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;&gt;&gt;|&nbsp;&nbsp;</button>
</chess-navigation>
<chess-movelist>
	<chess-move>
		<chess-move-number>1</chess-move-number>
		<chess-move-white>e4</chess-move-white>
		<chess-move-black>e5</chess-move-black>
	</chess-move>
	<chess-move>
		<chess-move-number>2</chess-move-number>
		<chess-move-white>♘f3</chess-move-white>
		<chess-move-black>♞c6</chess-move-black>
	</chess-move>
	<chess-move>
		<chess-move-number>3</chess-move-number>
		<chess-move-white>♘c3</chess-move-white>
		<chess-move-black>d6</chess-move-black>
	</chess-move>
	<chess-move>
		<chess-move-number>4</chess-move-number>
		<chess-move-white>♗c4</chess-move-white>
		<chess-move-black>♝g4</chess-move-black>
	</chess-move>
	<chess-move>
		<chess-move-number>5</chess-move-number>
		<chess-move-white>d3</chess-move-white>
		<chess-move-black class="answer-right">♛f6</chess-move-black>
	</chess-move>
	<chess-move>
		<chess-move-number>5</chess-move-number>
		<chess-move-white>d3</chess-move-white>
		<chess-move-black class="answer-wrong">♞g4</chess-move-black>
	</chess-move>
	<chess-move>
		<chess-move-number>5</chess-move-number>
		<chess-move-white>d3</chess-move-white>
		<chess-move-black></chess-move-black>
	</chess-move>
</chess-movelist>

<style lang="scss">
chess-navigation {
	display: grid;
	grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
}

chess-navigation button {
	padding: 0.5rem;
	border: none;
}

chess-movelist {
	display: grid;
	grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
	align-content: start;
	overflow-y: auto;
}

chess-move {
	grid-column: span 5;
	font-size: 14pt;
	display: grid;
	grid-template-columns: 1fr 2fr 2fr;
	justify-items: center;
}

chess-move-number, chess-move-white, chess-move-black, chess-navigation {
	border-bottom: 1px solid #ddd;
}

chess-move-number {
	background-color: #eee;
}

chess-move-number, chess-move-white, chess-move-black {
	justify-self: center;
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%;
	height: 100%;
}

chess-move-white, chess-move-black {
	border-right: 1px solid #ddd;
}

.answer-right {
	color: rgb(27, 80, 27);
	font-weight: bold;
}

.answer-wrong {
	color: rgb(172, 38, 38);
	font-weight: bold;
}
</style>
