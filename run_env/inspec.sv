`ifndef INSTR_MACROS
`define INSTR_MACROS 1

`define NO_INSTR 2'b00
`define WRITE_INSTR 2'b01
`define READ_INSTR 2'b10
`define MOVE_INSTR 2'b11
`endif
// Note that op[1] indicates if a read is involved and op[0] indicates if a write is involved

module inspec #(
    parameter DATA_WIDTH = 32,
    parameter BYTE_ADDR_WIDTH = 8,
    parameter BANKS_ADDR_WIDTH = 2,
    parameter INSTR_QUEUE_LEN = 8,
    localparam NUM_SWITCHES = (1 << BANKS_ADDR_WIDTH)
) (
    input clk,
    input rst,
    input [1:0] op,
    input [BYTE_ADDR_WIDTH+BANKS_ADDR_WIDTH-1:0] addr,
    input [DATA_WIDTH-1:0] din,
    output [DATA_WIDTH-1:0] dout
);
    // Data structures definition
    typedef struct packed {
        bit [1:0] op;
        bit [BANKS_ADDR_WIDTH-1:0] bank;
        bit [BYTE_ADDR_WIDTH-1:0] addr;
        bit [DATA_WIDTH-1:0] din;
    } instr_t;

    // Internal state
    instr_t current_instr, next_instr, arriving_instr;
    reg ready_for_next_instr;

    // IO
    reg read_next_instr;
    wire instr_wen, has_next_instr;
    wire [DATA_WIDTH-1:0] inter_switch_lr [0:NUM_SWITCHES-2];
    wire [DATA_WIDTH-1:0] inter_switch_rl [0:NUM_SWITCHES];

    // Probes
    `ifdef DEBUG_ON
        wire [DATA_WIDTH-1:0] inter_01 = inter_switch_lr[0];
        wire [DATA_WIDTH-1:0] inter_12 = inter_switch_lr[1];
        wire [DATA_WIDTH-1:0] inter_23 = inter_switch_lr[2];

        wire [DATA_WIDTH-1:0] inter_10 = inter_switch_rl[1];
        wire [DATA_WIDTH-1:0] inter_21 = inter_switch_rl[2];
        wire [DATA_WIDTH-1:0] inter_32 = inter_switch_rl[3];

        wire [1:0] current_op = current_instr.op;
        wire [BANKS_ADDR_WIDTH-1:0] current_bank = current_instr.bank;
        wire [BYTE_ADDR_WIDTH-1:0] current_addr = current_instr.addr;
        wire [DATA_WIDTH-1:0] current_din = current_instr.din;
        wire [BANKS_ADDR_WIDTH-1:0] next_bank = next_instr.bank;
        wire [DATA_WIDTH-1:0] next_din = next_instr.din;
        wire [BANKS_ADDR_WIDTH-1:0] arriving_bank = arriving_instr.bank;
        wire [DATA_WIDTH-1:0] arriving_din = arriving_instr.din;
    `endif

    // Instantiate instruction queue
    rw_queue #(.DATA_WIDTH(2+BANKS_ADDR_WIDTH+BYTE_ADDR_WIDTH+DATA_WIDTH), .LEN(INSTR_QUEUE_LEN), .DEF_TO_ZERO(1)) instr_queue (
        .clk(clk),
        .rst(rst),
        .read_next(read_next_instr),
        .wen(instr_wen),
        .data_in(arriving_instr),
        .data_out(current_instr),
        .peek_out(next_instr),
        .has_peek(has_next_instr)
    );

    `ifdef DEBUG_ON
        wire instr_queue_full = instr_queue.queue_full;
    `endif

    // Connect simple logic
    assign arriving_instr.op = op;
    assign arriving_instr.bank = addr[BYTE_ADDR_WIDTH +: BANKS_ADDR_WIDTH];
    assign arriving_instr.addr = addr[0 +: BYTE_ADDR_WIDTH];
    assign arriving_instr.din = din;

    // Readability ease
    wire [BANKS_ADDR_WIDTH-1:0] current_to_bank = current_instr.din[BYTE_ADDR_WIDTH +: BANKS_ADDR_WIDTH];
    wire [BYTE_ADDR_WIDTH-1:0] current_to_addr = current_instr.din[0 +: BYTE_ADDR_WIDTH];
    wire [BANKS_ADDR_WIDTH-1:0] next_to_bank = next_instr.din[BYTE_ADDR_WIDTH +: BANKS_ADDR_WIDTH];
    wire [BANKS_ADDR_WIDTH-1:0] next_to_addr = next_instr.din[0 +: BYTE_ADDR_WIDTH];

    // Generate switches
    genvar i;
    generate
    for (i=0 ; i < NUM_SWITCHES ; i++) begin
        wire sw_ren = current_instr.op[1] & (current_instr.bank == i);
        wire sw_wen = current_instr.op[0] & (current_instr.op[1] ? current_to_bank == i : current_instr.bank == i);
        wire sw_source = current_instr.op == `MOVE_INSTR ? current_instr.bank > i : 1'b0;
        wire [BYTE_ADDR_WIDTH-1:0] sw_addr = ((current_instr.op == `MOVE_INSTR) & (i == current_to_bank)) ? current_to_addr : current_instr.addr;
        wire [DATA_WIDTH-1:0] sw_left_i = (i == 0) ? current_instr.din : inter_switch_lr[(i==0 ? 0 : i-1)];

        switch #(.DATA_WIDTH(DATA_WIDTH), .BYTE_ADDR_WIDTH(BYTE_ADDR_WIDTH)) sw (
            .clk(clk),
            .ren(sw_ren),
            .wen(sw_wen),
            .source(sw_source),
            .addr(sw_addr),
            .left_i(sw_left_i),
            .right_i(inter_switch_rl[i+1])
        );
        
        assign inter_switch_rl[i] = sw.left_o;
        if (i == (NUM_SWITCHES-1))
            assign dout = sw.right_o;
        else
            assign inter_switch_lr[i] = sw.right_o;
    end
    endgenerate

    // Store next instruction
    assign instr_wen = (arriving_instr.op != `NO_INSTR);
    // Wait one clock cycle after a write/move instruction
    /* assign read_next_instr = rst ? 0 : (
        current_instr.op[0] ? (has_next_instr ? next_instr.bank : arriving_instr.bank) != (current_instr.op[1] ? current_to_bank : current_instr.bank) : 1
    ); */
    always @(negedge clk) begin
        read_next_instr = rst ? 0 : (
            current_instr.op[0] ? (has_next_instr ? next_instr.bank : arriving_instr.bank) != (current_instr.op[1] ? current_to_bank : current_instr.bank) : 1
        );
    end

    // Print warning if queue is full
    `ifdef DEBUG_ON
    wire is_problem = (instr_queue_full & instr_wen & (~rst) & (~read_next_instr));
    always @(posedge is_problem)
        $warning("Queue is full at time %t", $time);
    `endif
endmodule
