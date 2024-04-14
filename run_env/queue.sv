
module rw_queue #(
    parameter DATA_WIDTH = 16,
    parameter shortint unsigned LEN = 3,
    parameter DEF_TO_ZERO = 1,
    localparam COUNTER_LEN = $clog2(LEN) + 1
) (
    input clk,
    input rst,
    input read_next,
    input wen,
    input [DATA_WIDTH-1:0] data_in,
    output reg [DATA_WIDTH-1:0] data_out,
    output reg [DATA_WIDTH-1:0] peek_out,
    output reg has_peek,
    output queue_full
);
    // Internal state
    reg [COUNTER_LEN-1:0] head_d [1:0];
    reg [COUNTER_LEN-1:0] tail_d [1:0];
    reg [LEN-1:0] n_elem_d [1:0];
    reg [DATA_WIDTH-1:0] data [LEN-1:0];
    reg state;

    // Probes for debugging purposes
    `ifdef DEBUG_ON
        wire [DATA_WIDTH-1:0] data_0 = data[0];
        wire [DATA_WIDTH-1:0] data_1 = data[1];
        wire [DATA_WIDTH-1:0] data_2 = data[2];
    `endif

    // Constant outputs and shortcuts
    wire [COUNTER_LEN-1:0] head = head_d[state];
    wire [COUNTER_LEN-1:0] tail = tail_d[state];
    wire [LEN-1:0] n_elem = n_elem_d[state];

    assign queue_full = n_elem[LEN-1];

    wire do_write = wen & (read_next | (~queue_full));
    wire do_read = read_next & (wen | n_elem[0]);

    wire [COUNTER_LEN-1:0] inc_head = (head == (LEN-1) ? 0 : head + 1);
    wire [COUNTER_LEN-1:0] inc_tail = (tail == (LEN-1) ? 0 : tail + 1);
    // wire [COUNTER_LEN-1:0] next_head = do_read ? inc_head : head;
    // wire [COUNTER_LEN-1:0] next_tail = do_write ? inc_tail : tail;
    /*counter #(.WIDTH(COUNTER_LEN), .MOD(LEN)) head_counter (
        .in(head),
        .increment(do_read),
        .out(next_head)
    );
    counter #(.WIDTH(COUNTER_LEN), .MOD(LEN)) tail_counter (
        .in(tail),
        .increment(do_write),
        .out(next_tail)
    );*/

    always @(posedge clk) begin
        if (rst) begin
            data_out <= DEF_TO_ZERO ? '0 : 'z;
            has_peek <= 0;

            head_d[0] <= 0;
            tail_d[0] <= 0;
            n_elem_d[0] <= 0;

            state = 0;
        end
        else begin
            // Read - Write logic
            if (wen & read_next & (~n_elem[0]))
                data_out <= data_in;
            else if (do_read)
                data_out <= data[head];
            else
                data_out <= DEF_TO_ZERO ? '0 : 'z;
            if (do_write) begin
                data[tail] <= data_in;
            end

            // Prepare for the next clock cycle
            head_d[~state] <= do_read ? inc_head : head;
            tail_d[~state] <= do_write ? inc_tail : tail;
            case ({do_read, do_write})
                2'b01: n_elem_d[~state] <= (n_elem << 1) | 1;
                2'b10: n_elem_d[~state] <= (n_elem >> 1);
                default: n_elem_d[~state] <= n_elem;
            endcase

            // Peek logic
            has_peek <= n_elem[1] | (~read_next & n_elem[0]) | (~read_next & do_write) | (do_write & n_elem[0]);
            if (do_write & (tail == head))
                peek_out <= data_in;
            else
                peek_out <= data[do_read ? inc_head : head];

            state = ~state;
        end
    end
endmodule

module counter #(
    parameter WIDTH = 8,
    parameter shortint unsigned MOD = 3
) (
    input [WIDTH-1:0] in,
    input increment,
    output [WIDTH-1:0] out
);
    wire [WIDTH-1:0] sum;
    wire [WIDTH-2:0] carry;

    assign out = increment ? (in == (MOD - 1) ? 0 : sum) : in;

    // Simplified adder: increases the input by 1
    assign sum[0] = ~in[0];
    assign carry[0] = in[0];
    generate
        genvar i;
        for (i = 1; i < WIDTH; i = i + 1) begin
            assign sum[i] = in[i] ^ carry[i-1];
            if (i < WIDTH - 1)
                assign carry[i] = in[i] & carry[i-1];
        end
    endgenerate
endmodule

module timed_queue #(
    parameter DATA_WIDTH = 16,
    parameter LEN = 5 // index must fit in an unsigned shortint (16 bits)
) (
    input clk,
    input rst,
    input wen,
    input shortint unsigned delay,
    input [DATA_WIDTH-1:0] data_in,
    output [DATA_WIDTH-1:0] data_out,
    output has_data_out
);
    // Internal state
    shortint unsigned head, next_head;
    reg [DATA_WIDTH-1:0] data [LEN-1:0];
    reg [LEN-1:0] has_data;

    // Probes for debugging purposes
    `ifdef DEBUG_ON        
        wire [DATA_WIDTH-1:0] data_0 = data[0];
        wire [DATA_WIDTH-1:0] data_1 = data[1];
        wire [DATA_WIDTH-1:0] data_2 = data[2];
    `endif


    /*
        Logic
    */

    assign data_out = data[next_head];
    assign has_data_out = has_data[0];

    always @(posedge clk) begin
        if (wen)
            data[(head + 1 + delay) % LEN] <= data_in;
        has_data <= rst ? '0 : ((wen << delay) | (has_data >> 1));
        next_head <= rst ? 0 : (head + 1) % LEN;
    end

    always @(negedge clk) begin
        head <= next_head;
    end
endmodule
