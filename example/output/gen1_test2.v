`timescale 1ns / 1ps

module testbench;
    reg clk;
    reg [2:0] in1;
    reg [4:0] in2;
    wire [4:0] out;

    module2 uut (
        .clk(clk),
        .in1(in1),
        .in2(in2),
        .out(out)
    );

    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, uut);

        // Initialize
        clk = 0;
        @(posedge clk);

        // Autogenerated code        @(posedge clk); in1 = 12'h100; in2 = 20'h720c9;
        @(posedge clk); in1 = 12'h727; in2 = 20'hc3375;
        @(posedge clk); in1 = 12'hd06; in2 = 20'hc7474;
        @(posedge clk); in1 = 12'hddf; in2 = 20'h53df7;
        @(posedge clk); in1 = 12'h578; in2 = 20'hbf7d5;
        @(posedge clk); in1 = 12'h209; in2 = 20'h545a5;
        @(posedge clk); in1 = 12'hbd5; in2 = 20'h2d02d;
        @(posedge clk); in1 = 12'h2cb; in2 = 20'h88316;
        @(posedge clk); in1 = 12'h5cc; in2 = 20'h5964b;
        @(posedge clk); in1 = 12'hfa6; in2 = 20'hab027;

        // Finish
        $finish();
    end

    always #1 clk = ~clk;
endmodule