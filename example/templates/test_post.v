        // Finish
        $finish();
    end

    always #1 clk = ~clk;
endmodule