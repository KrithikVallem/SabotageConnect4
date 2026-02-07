const EMPTY = 0;
const PLAYERS = {
    RED_NORMAL: 1,
    YELLOW_NORMAL: 2,
    RED_SABOTAGE: 3,
    YELLOW_SABOTAGE: 4
}
const PLAYERS_HTML_DESCRIPTIONS = {
    [PLAYERS.RED_NORMAL]: '<span class="red-team">Red Normal, </span><span class="red-team">Has Red Pieces</span>',
    [PLAYERS.YELLOW_NORMAL]: '<span class="yellow-team">Yellow Normal, </span><span class="yellow-team">Has Yellow Pieces</span>',
    [PLAYERS.RED_SABOTAGE]: '<span class="red-team">Red Spy, </span><span class="yellow-team">Has Yellow Pieces</span>',
    [PLAYERS.YELLOW_SABOTAGE]: '<span class="yellow-team">Yellow Spy, </span><span class="red-team">Has Red Pieces</span>',
}

const PLAYER_ORDER = [
    PLAYERS.RED_NORMAL,
    PLAYERS.YELLOW_SABOTAGE,
    PLAYERS.YELLOW_NORMAL,
    PLAYERS.RED_SABOTAGE,
]

class SabotageConnect4 {
    board = [];
    currentPlayerIndex = 0;
    gameOver = false;
    history = []; // stack of board states

    initBoard() {
        const ROWS = 6;
        const COLS = 7;
        for (let r = 0; r < ROWS; r++) {
            this.board[r] = [];
            for (let c = 0; c < COLS; c++) {
                this.board[r][c] = EMPTY;
            }
        }
        this.history = [];
    }

    saveState() {
        // Deep copy board and push to history
        this.history.push(this.board.map(row => [...row]));
    }

    undo() {
        if (this.history.length === 0) return;
        this.board = this.history.pop();
        this.currentPlayerIndex = (this.currentPlayerIndex - 1 + PLAYER_ORDER.length) % PLAYER_ORDER.length;
        this.gameOver = false;
        this.renderBoard();
        this.updateUndoButton();
        this.updatePlayerInfo();
    }

    updateUndoButton() {
        const btn = document.getElementById('undoBtn');
        if (btn) btn.disabled = this.history.length === 0;
    }

    addEventHandlers() {
        const cols = document.querySelectorAll('.col');
        cols.forEach((col, colIndex) => {
            col.addEventListener('click', () => {
                this.handleColumnClick(colIndex);
            });
        });

        const undoBtn = document.getElementById('undoBtn');
        if (undoBtn) undoBtn.addEventListener('click', () => this.undo());

        const newGameBtn = document.getElementById('newGameBtn');
        if (newGameBtn) {
            newGameBtn.addEventListener('click', () => {
                if (confirm('Start a new game? This will reset the board.')) {
                window.location.reload();
                }
            });
        }
    }

    handleColumnClick(colIndex) {
        if (this.gameOver) return;

        const rows = this.board.length;
        for (let r = rows - 1; r >= 0; r--) {
            if (this.board[r][colIndex] === EMPTY) {
                this.saveState(); // save before making move
                this.board[r][colIndex] = PLAYER_ORDER[this.currentPlayerIndex];
                this.renderBoard();
                
                const winner = this.detectWinner();
                if (winner) {
                    this.gameOver = true;
                    const teamName = winner === 1 ? 'Red' : 'Yellow';
                    alert(`${teamName} team wins!`);
                } else {
                    this.currentPlayerIndex = (this.currentPlayerIndex + 1) % PLAYER_ORDER.length;
                    this.updatePlayerInfo();
                }
                this.updateUndoButton();
                break;
            }
        }
    }

    renderBoard() {
        const cols = document.querySelectorAll('.col');
        cols.forEach((col, colIndex) => {
            const cells = col.querySelectorAll('.cell');
            cells.forEach((cell, rowIndex) => {
                const cellValue = this.board[rowIndex][colIndex];
                cell.classList.remove('red-team', 'yellow-team', 'spy');
                if (cellValue === PLAYERS.RED_NORMAL) {
                    cell.classList.add('red-team');
                } else if (cellValue === PLAYERS.YELLOW_NORMAL) {
                    cell.classList.add('yellow-team');
                } else if (cellValue === PLAYERS.RED_SABOTAGE) {
                    cell.classList.add('red-team', 'spy');
                } else if (cellValue === PLAYERS.YELLOW_SABOTAGE) {
                    cell.classList.add('yellow-team', 'spy');
                }
            });
        });
    }

    detectWinner() {
        const rows = this.board.length;
        const cols = this.board[0].length;

        // Remember, Sabotage has opposite piece color
        const getPieceColor = (val) => {
            if (val === PLAYERS.RED_NORMAL || val === PLAYERS.YELLOW_SABOTAGE) return 1;
            if (val === PLAYERS.YELLOW_NORMAL || val === PLAYERS.RED_SABOTAGE) return 2;
            return 0;
        };

        const checkLine = (r, c, dr, dc) => {
            const initialPieceColor = getPieceColor(this.board[r][c]);
            if (initialPieceColor === 0) return false;
            for (let i = 1; i < 4; i++) {
                const nr = r + dr * i;
                const nc = c + dc * i;
                if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) return false;
                if (getPieceColor(this.board[nr][nc]) !== initialPieceColor) return false;
            }
            return true;
        };

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (checkLine(r, c, 0, 1)) return getPieceColor(this.board[r][c]);
                if (checkLine(r, c, 1, 0)) return getPieceColor(this.board[r][c]);
                if (checkLine(r, c, 1, 1)) return getPieceColor(this.board[r][c]);
                if (checkLine(r, c, 1, -1)) return getPieceColor(this.board[r][c]);
            }
        }

        return 0;
    }

    updatePlayerInfo() {
        const nameEl = document.getElementById('playerName');
        if (nameEl) {
            const currentPlayer = PLAYER_ORDER[this.currentPlayerIndex];
            nameEl.innerHTML = PLAYERS_HTML_DESCRIPTIONS[currentPlayer] || 'Unknown Player';
        }
    }

    constructor() {
        this.initBoard();
        this.renderBoard();
        this.addEventHandlers();
        this.updateUndoButton();
        this.updatePlayerInfo();
    }
}

function main() {
    const game = new SabotageConnect4();
}

main();